package io.github.supermonster003.autojs6.plugin.python.runtime.service

import android.os.IBinder
import android.os.RemoteException
import android.os.SystemClock
import io.github.supermonster003.autojs6.plugin.python.runtime.PythonRuntimeMetadata
import io.github.supermonster003.autojs6.plugin.python.runtime.execution.BufferedOutputRecord
import io.github.supermonster003.autojs6.plugin.python.runtime.execution.ChaquopyRuntime
import io.github.supermonster003.autojs6.plugin.python.runtime.execution.PythonInputDeliveryException
import io.github.supermonster003.autojs6.plugin.python.runtime.execution.PythonInputLimitExceededException
import io.github.supermonster003.autojs6.plugin.python.runtime.execution.PythonInputTimeoutException
import io.github.supermonster003.autojs6.plugin.python.runtime.execution.PythonOutputDeliveryException
import io.github.supermonster003.autojs6.plugin.python.runtime.execution.PythonOutputLimitExceededException
import io.github.supermonster003.autojs6.plugin.python.runtime.execution.PythonRunOutcome
import io.github.supermonster003.autojs6.plugin.python.runtime.process.ProcessRetirement
import io.github.supermonster003.autojs6.plugin.python.runtime.security.HostCallerVerifier
import io.github.supermonster003.autojs6.plugin.python.runtime.transport.HostCapabilitySnapshot
import io.github.supermonster003.autojs6.plugin.python.runtime.transport.OwnedParcelFileDescriptors
import io.github.supermonster003.autojs6.plugin.python.runtime.transport.OutputArtifactWorkspace
import io.github.supermonster003.autojs6.plugin.python.runtime.transport.PreparedOutputArtifacts
import io.github.supermonster003.autojs6.plugin.python.runtime.transport.SourceSnapshot
import io.github.supermonster003.autojs6.plugin.python.runtime.transport.StdinSnapshot
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
import org.autojs.plugin.python.runtime.api.PythonInputEcho
import org.autojs.plugin.python.runtime.api.PythonInputPrompt
import org.autojs.plugin.python.runtime.api.PythonInputReply
import org.autojs.plugin.python.runtime.api.PythonPromptId
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
    private val startLease = SessionStartLease(scheduler, START_LEASE_MILLIS, ::startLeaseExpired)

    private var outstandingCredits = 0
    private var nextSequence = PythonRuntimeMetadata.FIRST_OUTPUT_SEQUENCE
    private var stdoutBytes = 0L
    private var stderrBytes = 0L
    private var stdoutChunks = 0L
    private var stderrChunks = 0L
    private var pendingInput: PendingInput? = null
    private var nextInputPromptId = 1L
    private var inputPromptCount = 0

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
            startLease.disarm()
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

    override fun replyInput(reply: ByteArray?) {
        callerVerifier.enforceSessionOwner(ownerUid)
        val decoded = try {
            PythonRuntimeCodec.decodeInputReply(
                requireNotNull(reply) { "Python input reply is null" },
            )
        } catch (_: RuntimeException) {
            hardRetire()
            return
        }
        var invalid = false
        synchronized(signal) {
            if (state.get() == State.TERMINAL || state.get() == State.CLOSED) return
            val pending = pendingInput
            if (
                state.get() != State.STARTED ||
                pending == null ||
                pending.reply != null ||
                decoded.requestId != request.requestId ||
                decoded.promptId != pending.prompt.promptId ||
                decoded.value?.toByteArray(Charsets.UTF_8)?.size?.let {
                    it > pending.prompt.maxReplyBytes
                } == true
            ) {
                invalid = true
            } else {
                pending.reply = decoded
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

    fun armStartLease(): Boolean = synchronized(callbackOrder) {
        state.get() == State.CREATED && startLease.arm()
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
        startLease.close()
        deadlineFuture?.cancel(false)
        terminalLeaseFuture?.cancel(false)
        workerFuture?.cancel(true)
        descriptors.close()
        inputs.getAndSet(null)?.close()
        synchronized(signal) {
            pendingInput = null
            signal.notifyAll()
        }
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

        val outputArtifactWorkspace = try {
            request.resultPolicy
                ?.takeIf { it.maxArtifacts > 0 }
                ?.let {
                    OutputArtifactWorkspace.create(
                        runtime.outputArtifactParentDirectory,
                        request.requestId,
                    )
                }
        } catch (_: Exception) {
            if (!isStopped()) {
                finishFailure(
                    PythonErrorCode.STORAGE_EXHAUSTED,
                    PythonFailurePhase.RESULT,
                    "Python output artifact workspace could not be created",
                )
            }
            return
        }
        try {
            val outcome = try {
                val executionInputs = checkNotNull(inputs.get())
                val source = executionInputs.source.copyBytes()
                val hostCapabilitySnapshot = executionInputs.hostCapabilities?.copyBytes()
                val stdinSnapshot = executionInputs.stdin?.copyBytes()
                try {
                    runtime.execute(
                        source = source,
                        request = request,
                        workspaceRoot = executionInputs.workspace?.root,
                        hostCapabilitySnapshot = hostCapabilitySnapshot,
                        stdinSnapshot = stdinSnapshot,
                        onOutput = ::emitOutput,
                        onInput = request.interactiveInput?.let { ::requestInput },
                        outputArtifactRoot = outputArtifactWorkspace?.root,
                    )
                } finally {
                    source.fill(0)
                    hostCapabilitySnapshot?.fill(0)
                    stdinSnapshot?.fill(0)
                }
            } catch (_: InterruptedException) {
                Thread.currentThread().interrupt()
                return
            } catch (_: PythonOutputLimitExceededException) {
                if (!isStopped()) {
                    finishFailure(
                        PythonErrorCode.OUTPUT_LIMIT_EXCEEDED,
                        PythonFailurePhase.OUTPUT,
                        "Python output exceeded the negotiated limit",
                    )
                }
                return
            } catch (_: PythonOutputDeliveryException) {
                if (!isStopped()) {
                    finishFailure(
                        PythonErrorCode.INTERNAL,
                        PythonFailurePhase.OUTPUT,
                        "Python output delivery failed",
                    )
                }
                return
            } catch (_: PythonInputTimeoutException) {
                if (!isStopped()) {
                    finishFailure(
                        PythonErrorCode.INPUT_TIMEOUT,
                        PythonFailurePhase.INTERACTIVE_INPUT,
                        "Python interactive input reply timed out",
                    )
                }
                return
            } catch (_: PythonInputLimitExceededException) {
                if (!isStopped()) {
                    finishFailure(
                        PythonErrorCode.INPUT_LIMIT_EXCEEDED,
                        PythonFailurePhase.INTERACTIVE_INPUT,
                        "Python interactive input exceeded the negotiated limit",
                    )
                }
                return
            } catch (_: PythonInputDeliveryException) {
                if (!isStopped()) {
                    finishFailure(
                        PythonErrorCode.INTERNAL,
                        PythonFailurePhase.INTERACTIVE_INPUT,
                        "Python interactive input delivery failed",
                    )
                }
                return
            } catch (_: Exception) {
                if (!isStopped()) {
                    finishFailure(
                        PythonErrorCode.INTERNAL,
                        PythonFailurePhase.EXECUTION,
                        "Python bootstrap failed",
                    )
                }
                return
            }
            inputs.getAndSet(null)?.close()
            if (isStopped()) return

            when (outcome) {
                is PythonRunOutcome.Completed -> runCatching {
                    val prepared = if (outputArtifactWorkspace == null) {
                        require(outcome.artifactPaths.isEmpty()) {
                            "Python bootstrap returned artifacts without a negotiated output workspace"
                        }
                        null
                    } else {
                        outputArtifactWorkspace.prepare(
                            paths = outcome.artifactPaths,
                            policy = checkNotNull(request.resultPolicy),
                            shouldStop = ::isStopped,
                        )
                    }
                    try {
                        finishResult(outcome, prepared)
                    } catch (error: Throwable) {
                        prepared?.close()
                        throw error
                    }
                }
                is PythonRunOutcome.Failed -> runCatching { finishPythonException(outcome) }
                is PythonRunOutcome.OutputLimitExceeded -> runCatching {
                    finishFailure(
                        PythonErrorCode.OUTPUT_LIMIT_EXCEEDED,
                        PythonFailurePhase.OUTPUT,
                        "Python output exceeded the negotiated limit",
                    )
                }
                PythonRunOutcome.Stopped -> runCatching {
                    finishFailure(
                        PythonErrorCode.INTERNAL,
                        PythonFailurePhase.OUTPUT,
                        "Python output stopped without a session terminal",
                        retireProcess = true,
                    )
                }
            }.onFailure {
                if (state.get() == State.STARTED) {
                    finishFailure(
                        PythonErrorCode.OUTPUT_ARTIFACT_REJECTED,
                        PythonFailurePhase.RESULT,
                        "Python explicit result or output artifact was rejected",
                    )
                }
            }
        } finally {
            outputArtifactWorkspace?.close()
        }
    }

    private fun stageInputs(): ExecutionInputs? {
        var source: SourceSnapshot? = null
        var workspace: WorkspaceSnapshot? = null
        var hostCapabilities: HostCapabilitySnapshot? = null
        var stdin: StdinSnapshot? = null
        try {
            try {
                descriptors.consume(request.source) { descriptor ->
                    source = SourceSnapshot.materialize(
                        reference = request.source,
                        descriptor = descriptor,
                        maximumLengthBytes = PythonRuntimeMetadata.capabilities.limits.maxSourceBytes,
                        shouldStop = ::isStopped,
                        requireUtf8Source = true,
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
                                entryMode = request.entryMode,
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

            request.stdin?.let { stdinReference ->
                try {
                    descriptors.consume(stdinReference) { descriptor ->
                        stdin = StdinSnapshot.materialize(
                            reference = stdinReference,
                            descriptor = descriptor,
                            maximumLengthBytes = PythonRuntimeMetadata.capabilities.limits.maxStdinBytes,
                            shouldStop = ::isStopped,
                        )
                    }
                } catch (_: Exception) {
                    if (!isStopped()) {
                        finishFailure(
                            PythonErrorCode.STDIN_REJECTED,
                            PythonFailurePhase.INPUT_VALIDATION,
                            "Python stdin snapshot was rejected",
                        )
                    }
                    return null
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
            return ExecutionInputs(checkNotNull(source), workspace, stdin, hostCapabilities).also {
                source = null
                workspace = null
                stdin = null
                hostCapabilities = null
            }
        } finally {
            descriptors.close()
            hostCapabilities?.close()
            stdin?.close()
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
        val totalBytes = stdoutBytes + stderrBytes
        val totalChunks = stdoutChunks + stderrChunks
        if (
            totalBytes > request.maxOutputBytes - record.bytes.size.toLong() ||
            totalChunks >= request.maxOutputChunks
        ) {
            throw PythonOutputLimitExceededException()
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
    }

    private fun requestInput(promptText: String, echo: PythonInputEcho): PythonInputReply {
        val inputPolicy = checkNotNull(request.interactiveInput) {
            "Python bootstrap requested interactive input without authorization"
        }
        val pending = synchronized(signal) {
            if (state.get() != State.STARTED || Thread.currentThread().isInterrupted) {
                throw InterruptedException("Python interactive input stopped")
            }
            if (inputPromptCount >= inputPolicy.maxPrompts) {
                throw PythonInputLimitExceededException()
            }
            if (promptText.toByteArray(Charsets.UTF_8).size > inputPolicy.maxPromptBytes) {
                throw PythonInputLimitExceededException()
            }
            if (pendingInput != null || nextInputPromptId == Long.MAX_VALUE) {
                throw PythonInputLimitExceededException()
            }
            val prompt = PythonInputPrompt(
                requestId = request.requestId,
                promptId = PythonPromptId.fromLong(nextInputPromptId),
                text = promptText,
                echo = echo,
                maxReplyBytes = inputPolicy.maxReplyBytes,
                replyTimeoutMillis = inputPolicy.replyTimeoutMillis,
            ).also(PythonRuntimeValidation::validateInputPrompt)
            PendingInput(prompt).also {
                pendingInput = it
                inputPromptCount++
                nextInputPromptId++
            }
        }
        try {
            val encoded = PythonRuntimeCodec.encodeInputPrompt(pending.prompt)
            dispatchInputPromptAndWait { executionCallback.onInputPrompt(encoded) }
            val deadline = SystemClock.elapsedRealtime() + pending.prompt.replyTimeoutMillis
            return synchronized(signal) {
                while (state.get() == State.STARTED && pending.reply == null) {
                    val remaining = deadline - SystemClock.elapsedRealtime()
                    if (remaining <= 0L) throw PythonInputTimeoutException()
                    signal.wait(minOf(remaining, INPUT_WAIT_POLL_MILLIS))
                }
                if (state.get() != State.STARTED || Thread.currentThread().isInterrupted) {
                    throw InterruptedException("Python interactive input stopped")
                }
                pending.reply ?: throw PythonInputTimeoutException()
            }
        } finally {
            synchronized(signal) {
                if (pendingInput === pending) pendingInput = null
            }
        }
    }

    private fun awaitCredit(): Long? = synchronized(signal) {
        while (state.get() == State.STARTED && outstandingCredits == 0) signal.wait(100L)
        if (state.get() != State.STARTED) return@synchronized null
        outstandingCredits--
        nextSequence++
        nextSequence - 1L
    }

    private fun finishResult(
        outcome: PythonRunOutcome.Completed,
        prepared: PreparedOutputArtifacts?,
    ) {
        val result = PythonExecutionResult(
            requestId = request.requestId,
            exitCode = outcome.exitCode,
            elapsedMillis = elapsedMillis(),
            stdoutBytes = stdoutBytes,
            stderrBytes = stderrBytes,
            stdoutChunks = stdoutChunks,
            stderrChunks = stderrChunks,
            structuredJson = outcome.structuredJson,
            outputArtifacts = prepared?.artifacts.orEmpty(),
        ).also {
            PythonRuntimeValidation.validateResultAgainstPolicy(
                it,
                request.resultPolicy,
                prepared?.descriptors?.size ?: 0,
            )
        }
        val encoded = PythonRuntimeCodec.encodeExecutionResult(result)
        if (prepared == null) {
            finishTerminal { executionCallback.onResult(encoded, emptyArray()) }
        } else {
            finishTerminal(
                onUndelivered = prepared::close,
                callback = {
                    try {
                        executionCallback.onResult(encoded, prepared.descriptors)
                    } finally {
                        prepared.close()
                    }
                },
            )
        }
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

    private fun finishTerminal(
        retireProcess: Boolean = false,
        onUndelivered: () -> Unit = {},
        callback: () -> Unit,
    ) {
        synchronized(callbackOrder) {
            if (!state.compareAndSet(State.STARTED, State.TERMINAL)) {
                onUndelivered()
                return
            }
            deadlineFuture?.cancel(false)
            descriptors.close()
            inputs.getAndSet(null)?.close()
            synchronized(signal) {
                pendingInput = null
                signal.notifyAll()
            }
            callbackLane.dispatch(
                callback,
                onFailure = {
                    onUndelivered()
                    hardRetire()
                },
            )
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

    private fun startLeaseExpired() {
        synchronized(callbackOrder) {
            if (!state.compareAndSet(State.CREATED, State.CLOSED)) return
            cleanupClosed()
        }
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
        synchronized(signal) {
            pendingInput = null
            signal.notifyAll()
        }
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

    private fun dispatchOutputAndWait(callback: () -> Unit) =
        dispatchSessionCallbackAndWait("Python output delivery stopped", callback)

    private fun dispatchInputPromptAndWait(callback: () -> Unit) =
        dispatchSessionCallbackAndWait("Python interactive input delivery stopped", callback)

    private fun dispatchSessionCallbackAndWait(stoppedMessage: String, callback: () -> Unit) {
        val done = CountDownLatch(1)
        val failure = AtomicReference<Throwable?>()
        synchronized(callbackOrder) {
            if (state.get() != State.STARTED) throw InterruptedException(stoppedMessage)
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
        const val START_LEASE_MILLIS = 5_000L
        const val INPUT_WAIT_POLL_MILLIS = 100L
    }

    private class ExecutionInputs(
        val source: SourceSnapshot,
        val workspace: WorkspaceSnapshot?,
        val stdin: StdinSnapshot?,
        val hostCapabilities: HostCapabilitySnapshot?,
    ) : AutoCloseable {
        override fun close() {
            runCatching { hostCapabilities?.close() }
            runCatching { stdin?.close() }
            runCatching { workspace?.close() }
            runCatching { source.close() }
        }
    }

    private class PendingInput(
        val prompt: PythonInputPrompt,
        var reply: PythonInputReply? = null,
    )
}
