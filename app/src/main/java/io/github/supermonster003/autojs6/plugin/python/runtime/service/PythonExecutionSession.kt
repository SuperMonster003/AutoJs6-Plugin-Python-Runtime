package io.github.supermonster003.autojs6.plugin.python.runtime.service

import android.os.IBinder
import android.os.RemoteException
import android.os.SystemClock
import io.github.supermonster003.autojs6.plugin.python.runtime.PythonRuntimeMetadata
import io.github.supermonster003.autojs6.plugin.python.runtime.execution.BufferedOutputRecord
import io.github.supermonster003.autojs6.plugin.python.runtime.execution.ChaquopyRuntime
import io.github.supermonster003.autojs6.plugin.python.runtime.execution.PythonRunOutcome
import io.github.supermonster003.autojs6.plugin.python.runtime.process.ProcessRetirement
import io.github.supermonster003.autojs6.plugin.python.runtime.security.HostCallerVerifier
import io.github.supermonster003.autojs6.plugin.python.runtime.transport.HostCapabilitySnapshot
import io.github.supermonster003.autojs6.plugin.python.runtime.transport.OwnedParcelFileDescriptors
import io.github.supermonster003.autojs6.plugin.python.runtime.transport.SourceSnapshot
import io.github.supermonster003.autojs6.plugin.python.runtime.transport.WorkspaceSnapshot
import org.autojs.plugin.python.runtime.api.IPythonExecutionCallback
import org.autojs.plugin.python.runtime.api.IPythonExecutionSession
import org.autojs.plugin.python.runtime.api.IPythonSessionOpenCallback
import org.autojs.plugin.python.runtime.api.PythonCancellationReason
import org.autojs.plugin.python.runtime.api.PythonErrorCode
import org.autojs.plugin.python.runtime.api.PythonExecutionCancellation
import org.autojs.plugin.python.runtime.api.PythonExecutionError
import org.autojs.plugin.python.runtime.api.PythonExecutionRequest
import org.autojs.plugin.python.runtime.api.PythonExecutionResult
import org.autojs.plugin.python.runtime.api.PythonFailurePhase
import org.autojs.plugin.python.runtime.api.PythonOutputChunk
import org.autojs.plugin.python.runtime.api.PythonOutputStream
import org.autojs.plugin.python.runtime.api.PythonRuntimeCodec
import org.autojs.plugin.python.runtime.api.PythonRuntimeValidation
import org.autojs.plugin.python.runtime.api.PythonSessionStarted
import java.util.concurrent.CountDownLatch
import java.util.concurrent.ExecutorService
import java.util.concurrent.Future
import java.util.concurrent.RejectedExecutionException
import java.util.concurrent.ScheduledExecutorService
import java.util.concurrent.TimeUnit
import java.util.concurrent.atomic.AtomicBoolean
import java.util.concurrent.atomic.AtomicReference

internal class PythonExecutionSession(
    private val ownerUid: Int,
    private val request: PythonExecutionRequest,
    private val descriptors: OwnedParcelFileDescriptors,
    private val admissionCallback: IPythonSessionOpenCallback,
    private val executionCallback: IPythonExecutionCallback,
    private val callerVerifier: HostCallerVerifier,
    private val runtime: ChaquopyRuntime,
    private val worker: ExecutorService,
    private val scheduler: ScheduledExecutorService,
    private val callbackLane: SerialCallbackLane,
    private val retirement: ProcessRetirement,
    private val runtimeGeneration: Long,
    private val onReleased: (PythonExecutionSession) -> Unit,
) : IPythonExecutionSession.Stub() {
    private enum class State { CREATED, STARTED, TERMINAL, CLOSED }

    private val state = AtomicReference(State.CREATED)
    private val dispatched = AtomicBoolean(false)
    private val released = AtomicBoolean(false)
    private val callbackDeathsLinked = AtomicBoolean(false)
    // Serializes lifecycle transitions with callback enqueueing; never hold it while waiting for a callback.
    private val callbackOrder = java.lang.Object()
    private val signal = java.lang.Object()
    private val admissionBinder = admissionCallback.asBinder()
    private val executionBinder = executionCallback.asBinder()
    private val deathRecipient = IBinder.DeathRecipient(::callbackDied)
    private val createdAtMillis = SystemClock.elapsedRealtime()

    @Volatile private var workerFuture: Future<*>? = null
    @Volatile private var deadlineFuture: Future<*>? = null
    @Volatile private var terminalLeaseFuture: Future<*>? = null
    @Volatile private var encodedStarted: ByteArray? = null
    private val inputs = AtomicReference<ExecutionInputs?>()

    private var outstandingCredits = 0
    private var nextSequence = PythonRuntimeMetadata.FIRST_OUTPUT_SEQUENCE
    private var stdoutBytes = 0L
    private var stderrBytes = 0L
    private var stdoutChunks = 0L
    private var stderrChunks = 0L

    override fun start() {
        callerVerifier.enforceSessionOwner(ownerUid)
        val encodedStarted = try {
            val started = PythonSessionStarted(
                requestId = request.requestId,
                protocolVersion = request.protocolVersion,
                pythonVersion = PythonRuntimeMetadata.PYTHON_VERSION,
                firstOutputSequence = PythonRuntimeMetadata.FIRST_OUTPUT_SEQUENCE,
                effectiveMaxOutputBytes = request.maxOutputBytes,
                effectiveMaxOutputChunkBytes = request.maxOutputChunkBytes,
                effectiveMaxOutputChunks = request.maxOutputChunks,
                runtimeGeneration = runtimeGeneration,
            ).also(PythonRuntimeValidation::validateStarted)
            PythonRuntimeCodec.encodeSessionStarted(started)
        } catch (_: RuntimeException) {
            hardRetire()
            return
        }
        synchronized(callbackOrder) {
            if (!state.compareAndSet(State.CREATED, State.STARTED)) return
            dispatched.set(true)
            this.encodedStarted = encodedStarted
            if (state.get() != State.STARTED) return
            try {
                deadlineFuture = scheduler.schedule(
                    ::deadlineReached,
                    request.timeoutMillis,
                    TimeUnit.MILLISECONDS,
                )
            } catch (_: RuntimeException) {
                finishFailure(
                    PythonErrorCode.INTERNAL,
                    PythonFailurePhase.RUNTIME_START,
                    "Runtime deadline scheduler unavailable",
                    retireProcess = true,
                )
                return
            }
            if (state.get() != State.STARTED) return
            try {
                workerFuture = worker.submit(::runExecution)
            } catch (_: RejectedExecutionException) {
                finishFailure(
                    PythonErrorCode.INTERNAL,
                    PythonFailurePhase.RUNTIME_START,
                    "Runtime worker unavailable",
                    retireProcess = true,
                )
            }
        }
    }

    override fun grantOutputCredits(count: Int) {
        callerVerifier.enforceSessionOwner(ownerUid)
        var invalid = false
        synchronized(signal) {
            if (state.get() != State.CREATED && state.get() != State.STARTED) return
            val maximum = PythonRuntimeMetadata.capabilities.limits.maxOutstandingOutputCredits
            if (count <= 0 || outstandingCredits > maximum - count) {
                invalid = true
            } else {
                outstandingCredits += count
                signal.notifyAll()
            }
        }
        if (invalid) hardRetire()
    }

    override fun cancel() {
        callerVerifier.enforceSessionOwner(ownerUid)
        synchronized(callbackOrder) {
            val previous = state.get()
            if (previous == State.TERMINAL || previous == State.CLOSED) return
            val encoded = try {
                val cancellation = PythonExecutionCancellation(
                    requestId = request.requestId,
                    reason = PythonCancellationReason.REQUESTED,
                    phase = PythonFailurePhase.CANCELLATION,
                    elapsedMillis = elapsedMillis(),
                ).also(PythonRuntimeValidation::validateCancellation)
                PythonRuntimeCodec.encodeCancellation(cancellation)
            } catch (_: RuntimeException) {
                hardRetire()
                return
            }
            state.set(State.TERMINAL)
            if (previous == State.STARTED) dispatched.set(true)
            finishCancellation(encoded, retireProcess = previous == State.STARTED)
        }
    }

    override fun close() {
        callerVerifier.enforceSessionOwner(ownerUid)
        synchronized(callbackOrder) {
            val previous = state.getAndSet(State.CLOSED)
            if (previous == State.CLOSED) return
            val shouldRetire = previous == State.STARTED || (previous == State.TERMINAL && dispatched.get())
            if (shouldRetire) retirement.retireAfterCallbackDrain()
            cleanupClosed()
        }
    }

    fun linkCallbackDeaths(): Boolean {
        if (!callbackDeathsLinked.compareAndSet(false, true)) return state.get() != State.CLOSED
        return try {
            admissionBinder.linkToDeath(deathRecipient, 0)
            executionBinder.linkToDeath(deathRecipient, 0)
            if (!admissionBinder.isBinderAlive || !executionBinder.isBinderAlive) {
                callbackDied()
                false
            } else {
                true
            }
        } catch (_: RemoteException) {
            callbackDied()
            false
        }
    }

    fun serviceDestroyed() {
        forceClose()
    }

    fun forceClose() {
        synchronized(callbackOrder) {
            val previous = state.getAndSet(State.CLOSED)
            if (previous == State.CLOSED) return
            cleanupClosed()
        }
    }

    private fun cleanupClosed() {
        deadlineFuture?.cancel(false)
        terminalLeaseFuture?.cancel(false)
        workerFuture?.cancel(true)
        descriptors.close()
        inputs.getAndSet(null)?.close()
        synchronized(signal) { signal.notifyAll() }
        unlinkCallbackDeaths()
        releaseOnce()
    }

    private fun runExecution() {
        val stagedInputs = stageInputs() ?: return
        synchronized(callbackOrder) {
            if (state.get() != State.STARTED) {
                stagedInputs.close()
                return
            }
            if (!inputs.compareAndSet(null, stagedInputs)) {
                stagedInputs.close()
                finishFailure(
                    PythonErrorCode.INTERNAL,
                    PythonFailurePhase.INPUT_VALIDATION,
                    "Python input snapshot ownership was already assigned",
                    retireProcess = true,
                )
                return
            }
        }

        if (!publishStartedAndWait() || isStopped()) return

        try {
            runtime.prepare()
        } catch (_: Exception) {
            if (!isStopped()) {
                finishFailure(PythonErrorCode.INTERNAL, PythonFailurePhase.RUNTIME_START, "CPython failed to start")
            }
            return
        }
        if (isStopped()) return

        val outcome = try {
            val executionInputs = checkNotNull(inputs.get())
            val source = executionInputs.source.copyBytes()
            val hostCapabilitySnapshot = executionInputs.hostCapabilities?.copyBytes()
            try {
                runtime.execute(
                    source = source,
                    request = request,
                    workspaceRoot = executionInputs.workspace?.root,
                    hostCapabilitySnapshot = hostCapabilitySnapshot,
                )
            } finally {
                source.fill(0)
                hostCapabilitySnapshot?.fill(0)
            }
        } catch (_: Exception) {
            if (!isStopped()) {
                finishFailure(PythonErrorCode.INTERNAL, PythonFailurePhase.EXECUTION, "Python bootstrap failed")
            }
            return
        }
        inputs.getAndSet(null)?.close()
        if (isStopped()) return

        try {
            outcome.output.forEach(::emitOutput)
        } catch (_: InterruptedException) {
            Thread.currentThread().interrupt()
            return
        } catch (_: Exception) {
            if (!isStopped()) {
                finishFailure(PythonErrorCode.INTERNAL, PythonFailurePhase.OUTPUT, "Python output delivery failed")
            }
            return
        }
        if (isStopped()) return

        when (outcome) {
            is PythonRunOutcome.Completed -> runCatching { finishResult(outcome.exitCode) }
            is PythonRunOutcome.Failed -> runCatching { finishPythonException(outcome) }
            is PythonRunOutcome.OutputLimitExceeded -> runCatching {
                finishFailure(
                    PythonErrorCode.OUTPUT_LIMIT_EXCEEDED,
                    PythonFailurePhase.OUTPUT,
                    "Python output exceeded the negotiated limit",
                )
            }
        }.onFailure {
            if (state.get() == State.STARTED) {
                finishFailure(PythonErrorCode.INTERNAL, PythonFailurePhase.EXECUTION, "Python outcome encoding failed")
            }
        }
    }

    private fun stageInputs(): ExecutionInputs? {
        var source: SourceSnapshot? = null
        var workspace: WorkspaceSnapshot? = null
        var hostCapabilities: HostCapabilitySnapshot? = null
        try {
            try {
                descriptors.consume(request.source) { descriptor ->
                    source = SourceSnapshot.materialize(
                        reference = request.source,
                        descriptor = descriptor,
                        maximumLengthBytes = PythonRuntimeMetadata.capabilities.limits.maxSourceBytes,
                        shouldStop = ::isStopped,
                    )
                }
            } catch (_: Exception) {
                if (!isStopped()) {
                    finishFailure(
                        PythonErrorCode.SOURCE_REJECTED,
                        PythonFailurePhase.INPUT_VALIDATION,
                        "Python source snapshot was rejected",
                    )
                }
                return null
            }
            if (isStopped()) return null

            request.workspaceArchive?.let { workspaceReference ->
                val sourceBytes = checkNotNull(source).copyBytes()
                try {
                    try {
                        descriptors.consume(workspaceReference) { descriptor ->
                            val limits = PythonRuntimeMetadata.capabilities.limits
                            workspace = WorkspaceSnapshot.materialize(
                                reference = workspaceReference,
                                descriptor = descriptor,
                                sourceReference = request.source,
                                sourceBytes = sourceBytes,
                                entryPoint = request.entryPoint,
                                workspaceParent = runtime.workspaceParentDirectory,
                                maximumArchiveBytes = limits.maxWorkspaceArchiveBytes,
                                maximumEntries = limits.maxWorkspaceEntries,
                                maximumUncompressedBytes = limits.maxWorkspaceUncompressedBytes,
                                shouldStop = ::isStopped,
                            )
                        }
                    } catch (_: Exception) {
                        if (!isStopped()) {
                            finishFailure(
                                PythonErrorCode.WORKSPACE_REJECTED,
                                PythonFailurePhase.INPUT_VALIDATION,
                                "Python workspace snapshot was rejected",
                            )
                        }
                        return null
                    }
                } finally {
                    sourceBytes.fill(0)
                }
            }
            if (isStopped()) return null

            request.hostCapabilitySnapshot?.let { capabilityReference ->
                try {
                    descriptors.consume(capabilityReference) { descriptor ->
                        hostCapabilities = HostCapabilitySnapshot.materialize(
                            reference = capabilityReference,
                            descriptor = descriptor,
                            maximumLengthBytes = PythonRuntimeMetadata.capabilities.limits
                                .maxHostCapabilitySnapshotBytes,
                            expectedExecutionId = request.requestId.toString(),
                            expectedEntryPoint = request.entryPoint,
                            expectedProjectFilesAvailable = request.workspaceArchive != null,
                            shouldStop = ::isStopped,
                        )
                    }
                } catch (_: Exception) {
                    if (!isStopped()) {
                        finishFailure(
                            PythonErrorCode.HOST_CAPABILITY_SNAPSHOT_REJECTED,
                            PythonFailurePhase.INPUT_VALIDATION,
                            "Host capability snapshot was rejected",
                        )
                    }
                    return null
                }
            }
            descriptors.close()
            if (isStopped()) return null
            return ExecutionInputs(checkNotNull(source), workspace, hostCapabilities).also {
                source = null
                workspace = null
                hostCapabilities = null
            }
        } finally {
            descriptors.close()
            hostCapabilities?.close()
            workspace?.close()
            source?.close()
        }
    }

    /**
     * Publishes `onStarted` only after the complete immutable input snapshot set has passed every
     * length, EOF, reliable-pipe, digest and workspace extraction check. The timeout still begins at the
     * first accepted [start], so an input-validation failure remains non-replayable even when it
     * terminates without `onStarted`.
     */
    private fun publishStartedAndWait(): Boolean {
        val done = CountDownLatch(1)
        val failure = AtomicReference<Throwable?>()
        synchronized(callbackOrder) {
            if (state.get() != State.STARTED) return false
            val payload = encodedStarted ?: run {
                finishFailure(
                    PythonErrorCode.INTERNAL,
                    PythonFailurePhase.RUNTIME_START,
                    "Runtime start metadata was unavailable",
                    retireProcess = true,
                )
                return false
            }
            callbackLane.dispatch(
                callback = {
                    executionCallback.onStarted(payload)
                    done.countDown()
                },
                onFailure = { error ->
                    failure.compareAndSet(null, error)
                    done.countDown()
                },
            )
        }
        try {
            done.await()
        } catch (_: InterruptedException) {
            Thread.currentThread().interrupt()
            if (state.get() == State.STARTED) hardRetire()
            return false
        }
        if (failure.get() != null) {
            hardRetire()
            return false
        }
        return state.get() == State.STARTED
    }

    private fun emitOutput(record: BufferedOutputRecord) {
        require(record.bytes.isNotEmpty() && record.bytes.size <= request.maxOutputChunkBytes) {
            "Python bootstrap output chunk violates the negotiated size"
        }
        val sequence = awaitCredit() ?: throw InterruptedException("Python output delivery stopped")
        val chunk = PythonOutputChunk(request.requestId, sequence, record.stream, record.bytes)
            .also(PythonRuntimeValidation::validateOutputChunk)
        dispatchOutputAndWait {
            val encoded = PythonRuntimeCodec.encodeOutputChunk(chunk)
            when (record.stream) {
                PythonOutputStream.STDOUT -> executionCallback.onStdout(encoded)
                PythonOutputStream.STDERR -> executionCallback.onStderr(encoded)
            }
        }
        when (record.stream) {
            PythonOutputStream.STDOUT -> {
                stdoutBytes += record.bytes.size
                stdoutChunks++
            }
            PythonOutputStream.STDERR -> {
                stderrBytes += record.bytes.size
                stderrChunks++
            }
        }
        require(stdoutBytes + stderrBytes <= request.maxOutputBytes)
        require(stdoutChunks + stderrChunks <= request.maxOutputChunks)
    }

    private fun awaitCredit(): Long? = synchronized(signal) {
        while (state.get() == State.STARTED && outstandingCredits == 0) signal.wait(100L)
        if (state.get() != State.STARTED) return@synchronized null
        outstandingCredits--
        nextSequence++
        nextSequence - 1L
    }

    private fun finishResult(exitCode: Int) {
        val result = PythonExecutionResult(
            requestId = request.requestId,
            exitCode = exitCode,
            elapsedMillis = elapsedMillis(),
            stdoutBytes = stdoutBytes,
            stderrBytes = stderrBytes,
            stdoutChunks = stdoutChunks,
            stderrChunks = stderrChunks,
        ).also(PythonRuntimeValidation::validateResult)
        val encoded = PythonRuntimeCodec.encodeExecutionResult(result)
        finishTerminal { executionCallback.onResult(encoded, emptyArray()) }
    }

    private fun finishPythonException(outcome: PythonRunOutcome.Failed) {
        val error = PythonExecutionError(
            requestId = request.requestId,
            code = PythonErrorCode.PYTHON_EXCEPTION,
            phase = PythonFailurePhase.EXECUTION,
            message = "Python execution raised an exception",
            retryableBeforeDispatch = false,
            exceptionType = outcome.exceptionType,
            exceptionMessage = outcome.exceptionMessage,
            traceback = outcome.traceback,
        ).also(PythonRuntimeValidation::validateExecutionError)
        val encoded = PythonRuntimeCodec.encodeExecutionError(error)
        finishTerminal { executionCallback.onFailed(encoded) }
    }

    private fun finishFailure(
        code: PythonErrorCode,
        phase: PythonFailurePhase,
        message: String,
        retireProcess: Boolean = false,
    ) {
        val error = PythonExecutionError(
            requestId = request.requestId,
            code = code,
            phase = phase,
            message = message,
            retryableBeforeDispatch = false,
        ).also(PythonRuntimeValidation::validateExecutionError)
        val encoded = PythonRuntimeCodec.encodeExecutionError(error)
        finishTerminal(retireProcess) { executionCallback.onFailed(encoded) }
    }

    private fun finishTerminal(retireProcess: Boolean = false, callback: () -> Unit) {
        synchronized(callbackOrder) {
            if (!state.compareAndSet(State.STARTED, State.TERMINAL)) return
            deadlineFuture?.cancel(false)
            descriptors.close()
            inputs.getAndSet(null)?.close()
            synchronized(signal) { signal.notifyAll() }
            callbackLane.dispatch(callback, onFailure = { hardRetire() })
            if (retireProcess) {
                retirement.retireAfterCallbackDrain()
                forceClose()
            } else {
                scheduleTerminalLease(::hardRetire)
            }
        }
    }

    private fun deadlineReached() {
        finishFailure(
            PythonErrorCode.TIMEOUT,
            PythonFailurePhase.EXECUTION,
            "Python execution exceeded its deadline",
            retireProcess = true,
        )
    }

    private fun callbackDied() {
        synchronized(callbackOrder) {
            val previous = state.getAndSet(State.CLOSED)
            if (previous == State.CLOSED) return
            val shouldRetire = previous == State.STARTED || (previous == State.TERMINAL && dispatched.get())
            if (shouldRetire) retirement.markRetiring()
            cleanupClosed()
            if (shouldRetire) retirement.retireNow()
        }
    }

    private fun hardRetire() {
        retirement.markRetiring()
        forceClose()
        retirement.retireNow()
    }

    private fun finishCancellation(encoded: ByteArray, retireProcess: Boolean) {
        deadlineFuture?.cancel(false)
        descriptors.close()
        inputs.getAndSet(null)?.close()
        synchronized(signal) { signal.notifyAll() }
        callbackLane.dispatch(
            callback = { executionCallback.onCancelled(encoded) },
            onFailure = { if (retireProcess) hardRetire() else forceClose() },
        )
        if (retireProcess) {
            retirement.retireAfterCallbackDrain()
            forceClose()
        } else {
            scheduleTerminalLease(::forceClose)
        }
    }

    private fun dispatchOutputAndWait(callback: () -> Unit) {
        val done = CountDownLatch(1)
        val failure = AtomicReference<Throwable?>()
        synchronized(callbackOrder) {
            if (state.get() != State.STARTED) throw InterruptedException("Python output delivery stopped")
            callbackLane.dispatch(
                callback = {
                    try {
                        callback()
                    } catch (error: Throwable) {
                        failure.compareAndSet(null, error)
                    } finally {
                        done.countDown()
                    }
                },
                onFailure = { error ->
                    failure.compareAndSet(null, error)
                    done.countDown()
                },
            )
        }
        done.await()
        failure.get()?.let { throw it }
    }

    private fun scheduleTerminalLease(action: () -> Unit) {
        try {
            terminalLeaseFuture = scheduler.schedule(action, TERMINAL_CLOSE_LEASE_MILLIS, TimeUnit.MILLISECONDS)
        } catch (_: RuntimeException) {
            if (dispatched.get()) hardRetire() else forceClose()
        }
    }

    private fun releaseOnce() {
        if (released.compareAndSet(false, true)) onReleased(this)
    }

    private fun unlinkCallbackDeaths() {
        if (!callbackDeathsLinked.compareAndSet(true, false)) return
        runCatching { admissionBinder.unlinkToDeath(deathRecipient, 0) }
        runCatching { executionBinder.unlinkToDeath(deathRecipient, 0) }
    }

    private fun isStopped(): Boolean = state.get() != State.STARTED || Thread.currentThread().isInterrupted

    private fun elapsedMillis(): Long = (SystemClock.elapsedRealtime() - createdAtMillis).coerceAtLeast(0L)

    private companion object {
        const val TERMINAL_CLOSE_LEASE_MILLIS = 30_000L
    }

    private class ExecutionInputs(
        val source: SourceSnapshot,
        val workspace: WorkspaceSnapshot?,
        val hostCapabilities: HostCapabilitySnapshot?,
    ) : AutoCloseable {
        override fun close() {
            runCatching { hostCapabilities?.close() }
            runCatching { workspace?.close() }
            runCatching { source.close() }
        }
    }
}
