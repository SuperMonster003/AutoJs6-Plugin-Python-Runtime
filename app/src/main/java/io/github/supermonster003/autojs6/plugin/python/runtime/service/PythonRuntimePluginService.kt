package io.github.supermonster003.autojs6.plugin.python.runtime.service

import android.app.Service
import android.content.ComponentName
import android.content.Intent
import android.os.DeadObjectException
import android.os.IBinder
import android.os.ParcelFileDescriptor
import io.github.supermonster003.autojs6.plugin.python.runtime.PythonRuntimeMetadata
import io.github.supermonster003.autojs6.plugin.python.runtime.execution.ChaquopyRuntime
import io.github.supermonster003.autojs6.plugin.python.runtime.process.ProcessRetirement
import io.github.supermonster003.autojs6.plugin.python.runtime.security.HostCallerVerifier
import io.github.supermonster003.autojs6.plugin.python.runtime.transport.OwnedParcelFileDescriptors
import io.github.supermonster003.autojs6.plugin.python.runtime.transport.PythonRequestEnvelope
import org.autojs.plugin.python.runtime.api.IPythonExecutionCallback
import org.autojs.plugin.python.runtime.api.IPythonRuntimeProvider
import org.autojs.plugin.python.runtime.api.IPythonSessionOpenCallback
import org.autojs.plugin.python.runtime.api.PythonErrorCode
import org.autojs.plugin.python.runtime.api.PythonExecutionError
import org.autojs.plugin.python.runtime.api.PythonFailurePhase
import org.autojs.plugin.python.runtime.api.PythonRuntimeCodec
import org.autojs.plugin.python.runtime.api.PythonRuntimeContract
import org.autojs.plugin.python.runtime.api.PythonRuntimeContractException
import org.autojs.plugin.python.runtime.api.PythonRuntimeContractViolation
import org.autojs.plugin.python.runtime.api.PythonRuntimeValidation
import java.security.SecureRandom
import java.util.concurrent.ArrayBlockingQueue
import java.util.concurrent.ConcurrentHashMap
import java.util.concurrent.Executors
import java.util.concurrent.ThreadPoolExecutor
import java.util.concurrent.TimeUnit

class PythonRuntimePluginService : Service() {
    private lateinit var callerVerifier: HostCallerVerifier
    private lateinit var worker: ThreadPoolExecutor
    private lateinit var scheduler: java.util.concurrent.ScheduledExecutorService
    private lateinit var callbackLane: SerialCallbackLane
    private lateinit var runtime: ChaquopyRuntime
    private lateinit var retirement: ProcessRetirement
    private val sessionGate = SingleActiveSessionGate<PythonExecutionSession>()
    private val sessions = ConcurrentHashMap.newKeySet<PythonExecutionSession>()
    private val runtimeGeneration: Long = generateRuntimeGeneration()

    override fun onCreate() {
        super.onCreate()
        callerVerifier = HostCallerVerifier(this)
        worker = ThreadPoolExecutor(
            1,
            1,
            0L,
            TimeUnit.MILLISECONDS,
            ArrayBlockingQueue(1),
            { runnable -> Thread(runnable, "python-runtime-worker").apply { isDaemon = true } },
            ThreadPoolExecutor.AbortPolicy(),
        )
        scheduler = Executors.newSingleThreadScheduledExecutor { runnable ->
            Thread(runnable, "python-runtime-deadline").apply { isDaemon = true }
        }
        callbackLane = SerialCallbackLane()
        runtime = ChaquopyRuntime(this)
        retirement = ProcessRetirement(
            scheduler = scheduler,
            callbackDrain = callbackLane,
            markGenerationRetiring = { sessionGate.markRetiring() },
        )
        // Deliberately do not start CPython here. Admission and metadata calls stay lightweight.
    }

    override fun onBind(intent: Intent?): IBinder? {
        if (intent == null) return null
        val exactComponent = intent.component == ComponentName(this, PythonRuntimePluginService::class.java)
        val discoveryBind = intent.action == PythonRuntimeContract.RUNTIME_ACTION
        val pinnedBind = exactComponent && intent.action == null
        return binder.takeIf { discoveryBind || pinnedBind }
    }

    override fun onDestroy() {
        retirement.markRetiring()
        try {
            sessions.toList().forEach(PythonExecutionSession::serviceDestroyed)
            sessions.clear()
            callbackLane.close()
            worker.shutdownNow()
            scheduler.shutdownNow()
        } finally {
            try {
                super.onDestroy()
            } finally {
                retirement.retireNow()
            }
        }
    }

    private val binder = object : IPythonRuntimeProvider.Stub() {
        override fun getRuntimeInfo(): ByteArray {
            callerVerifier.enforceAllowedCaller()
            return PythonRuntimeCodec.encodeRuntimeInfo(PythonRuntimeMetadata.runtimeInfo)
        }

        override fun getCapabilities(): ByteArray {
            callerVerifier.enforceAllowedCaller()
            return PythonRuntimeCodec.encodeCapabilities(PythonRuntimeMetadata.capabilities)
        }

        override fun openSession(
            request: ByteArray?,
            descriptors: Array<out ParcelFileDescriptor?>?,
            admissionCallback: IPythonSessionOpenCallback?,
            executionCallback: IPythonExecutionCallback?,
        ) {
            var receiverCopiesTransferred = false
            var unassignedOwner: OwnedParcelFileDescriptors? = null
            var unadmittedSession: PythonExecutionSession? = null
            try {
                val ownerUid = callerVerifier.enforceAllowedCaller()
                val safeRequest = requireNotNull(request) { "Python request metadata is missing" }
                val safeAdmission = requireNotNull(admissionCallback) { "Python admission callback is missing" }
                val safeExecution = requireNotNull(executionCallback) { "Python execution callback is missing" }
                requireCallbacksAlive(safeAdmission, safeExecution)

                val requestId = try {
                    PythonRequestEnvelope.requireUniqueRequestId(safeRequest)
                } catch (error: Throwable) {
                    throw IllegalArgumentException("Python request has no unique valid correlation ID", error)
                }

                val decoded = try {
                    PythonRuntimeCodec.decodeExecutionRequest(safeRequest.copyOf()).also { value ->
                        val descriptorCount = descriptors?.size
                            ?: throw IllegalArgumentException("Python descriptor array is missing")
                        require(descriptors.none { it == null }) { "Python descriptor array contains null" }
                        require(
                            value.protocolVersion >= PythonRuntimeMetadata.protocolMinVersion &&
                                value.protocolVersion <= PythonRuntimeMetadata.protocolVersion,
                        ) { "Python request protocol is outside the provider range" }
                        PythonRuntimeValidation.validateRequestAgainst(
                            request = value,
                            capabilities = PythonRuntimeMetadata.capabilities,
                            negotiatedVersion = value.protocolVersion,
                            descriptorCount = descriptorCount,
                        )
                    }
                } catch (error: Throwable) {
                    reject(
                        safeAdmission,
                        PythonExecutionError(
                            requestId = requestId,
                            code = admissionCode(error),
                            phase = admissionPhase(error),
                            message = "Python runtime session request was rejected",
                            retryableBeforeDispatch = true,
                        ),
                    )
                    return
                }
                if (sessionGate.isRetiring()) {
                    reject(
                        safeAdmission,
                        PythonExecutionError(
                            requestId = requestId,
                            code = PythonErrorCode.SESSION_OPEN_FAILED,
                            phase = PythonFailurePhase.SESSION_OPEN,
                            message = "Python runtime generation is retiring",
                            retryableBeforeDispatch = true,
                        ),
                    )
                    return
                }

                val incoming = checkNotNull(descriptors)
                val owned = try {
                    OwnedParcelFileDescriptors.takeReceiverCopies(incoming).also {
                        receiverCopiesTransferred = true
                        unassignedOwner = it
                    }
                } catch (_: Throwable) {
                    reject(
                        safeAdmission,
                        PythonExecutionError(
                            requestId = requestId,
                            code = PythonErrorCode.SESSION_OPEN_FAILED,
                            phase = PythonFailurePhase.SESSION_OPEN,
                            message = "Python descriptor ownership transfer failed",
                            retryableBeforeDispatch = true,
                        ),
                    )
                    return
                }

                val session = PythonExecutionSession(
                    ownerUid = ownerUid,
                    request = decoded,
                    descriptors = owned,
                    admissionCallback = safeAdmission,
                    executionCallback = safeExecution,
                    callerVerifier = callerVerifier,
                    runtime = runtime,
                    worker = worker,
                    scheduler = scheduler,
                    callbackLane = callbackLane,
                    retirement = retirement,
                    runtimeGeneration = runtimeGeneration,
                    onReleased = { released ->
                        sessionGate.release(released)
                        sessions.remove(released)
                    },
                )
                unassignedOwner = null
                unadmittedSession = session
                sessions += session
                if (!sessionGate.tryAcquire(session)) {
                    val generationRetiring = sessionGate.isRetiring()
                    sessions.remove(session)
                    session.forceClose()
                    reject(
                        safeAdmission,
                        PythonExecutionError(
                            requestId = requestId,
                            code = if (generationRetiring) {
                                PythonErrorCode.SESSION_OPEN_FAILED
                            } else {
                                PythonErrorCode.BUSY
                            },
                            phase = PythonFailurePhase.SESSION_OPEN,
                            message = if (generationRetiring) {
                                "Python runtime generation is retiring"
                            } else {
                                "Python runtime already has an active session"
                            },
                            retryableBeforeDispatch = true,
                        ),
                    )
                    return
                }
                if (sessionGate.isRetiring()) {
                    session.forceClose()
                    reject(
                        safeAdmission,
                        PythonExecutionError(
                            requestId = requestId,
                            code = PythonErrorCode.SESSION_OPEN_FAILED,
                            phase = PythonFailurePhase.SESSION_OPEN,
                            message = "Python runtime generation is retiring",
                            retryableBeforeDispatch = true,
                        ),
                    )
                    return
                }
                if (!session.linkCallbackDeaths()) {
                    session.forceClose()
                    throw DeadObjectException()
                }
                try {
                    safeAdmission.onOpened(session)
                    unadmittedSession = null
                } catch (error: Throwable) {
                    session.forceClose()
                    throw error
                }
            } finally {
                // Binder has already unmarshalled receiver-side copies before this method runs.
                unadmittedSession?.forceClose()
                unassignedOwner?.close()
                if (!receiverCopiesTransferred) OwnedParcelFileDescriptors.closeIncoming(descriptors)
            }
        }
    }

    private fun requireCallbacksAlive(
        admissionCallback: IPythonSessionOpenCallback,
        executionCallback: IPythonExecutionCallback,
    ) {
        if (!admissionCallback.asBinder().isBinderAlive || !executionCallback.asBinder().isBinderAlive) {
            throw DeadObjectException()
        }
    }

    private fun reject(callback: IPythonSessionOpenCallback, error: PythonExecutionError) {
        PythonRuntimeValidation.validateAdmissionError(error)
        callback.onRejected(PythonRuntimeCodec.encodeExecutionError(error))
    }

    private fun admissionCode(error: Throwable): PythonErrorCode = when {
        error is PythonRuntimeContractException &&
            error.violation == PythonRuntimeContractViolation.PROTOCOL_INCOMPATIBLE ->
            PythonErrorCode.UNSUPPORTED_PROTOCOL
        error is PythonRuntimeContractException &&
            error.violation == PythonRuntimeContractViolation.CAPABILITY_INCOMPATIBLE ->
            PythonErrorCode.UNSUPPORTED_CAPABILITY
        else -> PythonErrorCode.INVALID_REQUEST
    }

    private fun admissionPhase(error: Throwable): PythonFailurePhase = when (admissionCode(error)) {
        PythonErrorCode.UNSUPPORTED_PROTOCOL,
        PythonErrorCode.UNSUPPORTED_CAPABILITY,
        -> PythonFailurePhase.NEGOTIATION
        else -> PythonFailurePhase.SESSION_OPEN
    }

    private companion object {
        fun generateRuntimeGeneration(): Long {
            val random = SecureRandom()
            while (true) {
                val candidate = random.nextLong() and Long.MAX_VALUE
                if (candidate > 0L) return candidate
            }
        }
    }
}
