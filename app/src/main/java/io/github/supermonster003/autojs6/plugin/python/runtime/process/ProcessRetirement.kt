package io.github.supermonster003.autojs6.plugin.python.runtime.process

import android.os.Process
import java.util.concurrent.ScheduledExecutorService
import java.util.concurrent.ScheduledFuture
import java.util.concurrent.TimeUnit
import java.util.concurrent.atomic.AtomicBoolean
import java.util.concurrent.atomic.AtomicReference

/** A non-blocking FIFO acknowledgement that all previously accepted callbacks have returned. */
internal fun interface CallbackDrain {
    fun dispatchWhenDrained(callback: () -> Unit): Boolean
}

/** Retires only this plugin's dedicated runtime process. The host process is never addressed. */
internal class ProcessRetirement(
    private val scheduler: ScheduledExecutorService,
    private val callbackDrain: CallbackDrain,
    private val markGenerationRetiring: () -> Unit,
    private val killRuntimeProcess: () -> Unit = { Process.killProcess(Process.myPid()) },
    private val callbackDrainTimeoutMillis: Long = CALLBACK_DRAIN_TIMEOUT_MILLIS,
) {
    private val retiring = AtomicBoolean(false)
    private val drainRetirementStarted = AtomicBoolean(false)
    private val killTriggered = AtomicBoolean(false)
    private val fallback = AtomicReference<ScheduledFuture<*>?>()

    init {
        require(callbackDrainTimeoutMillis > 0L) { "Callback drain timeout must be positive" }
    }

    fun isRetiring(): Boolean = retiring.get()

    fun markRetiring() {
        // Close admission first. A concurrent openSession can either acquire before this
        // transition or observe RETIRING, but it cannot acquire a slot in a retiring generation.
        markGenerationRetiring()
        retiring.set(true)
    }

    fun retireAfterCallbackDrain() {
        markRetiring()
        if (!drainRetirementStarted.compareAndSet(false, true)) return

        val scheduledFallback = try {
            scheduler.schedule({ killOnce() }, callbackDrainTimeoutMillis, TimeUnit.MILLISECONDS)
        } catch (_: RuntimeException) {
            killOnce()
            return
        }
        if (!fallback.compareAndSet(null, scheduledFallback)) {
            scheduledFallback.cancel(false)
        }

        // FIFO placement is the acknowledgement: reaching this task proves that the terminal
        // callback and every callback accepted before it have returned. If the lane rejects the
        // acknowledgement, the already-armed bounded fallback remains authoritative.
        callbackDrain.dispatchWhenDrained(::killOnce)
    }

    fun retireNow() {
        markRetiring()
        killOnce()
    }

    private fun killOnce() {
        if (!killTriggered.compareAndSet(false, true)) return
        fallback.getAndSet(null)?.cancel(false)
        killRuntimeProcess()
    }

    internal fun hasTriggeredKill(): Boolean = killTriggered.get()

    private companion object {
        const val CALLBACK_DRAIN_TIMEOUT_MILLIS = 2_000L
    }
}
