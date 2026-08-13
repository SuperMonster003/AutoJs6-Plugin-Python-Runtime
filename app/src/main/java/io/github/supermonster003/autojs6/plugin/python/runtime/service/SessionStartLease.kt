package io.github.supermonster003.autojs6.plugin.python.runtime.service

import java.util.concurrent.Future
import java.util.concurrent.ScheduledExecutorService
import java.util.concurrent.TimeUnit
import java.util.concurrent.atomic.AtomicBoolean

/** Bounds the interval in which an opened session may retain its slot without start/close. */
internal class SessionStartLease(
    private val scheduler: ScheduledExecutorService,
    private val timeoutMillis: Long,
    private val onExpired: () -> Unit,
) : AutoCloseable {
    private val armed = AtomicBoolean(false)

    @Volatile
    private var future: Future<*>? = null

    fun arm(): Boolean {
        if (!armed.compareAndSet(false, true)) return false
        return try {
            future = scheduler.schedule(
                {
                    if (armed.compareAndSet(true, false)) onExpired()
                },
                timeoutMillis,
                TimeUnit.MILLISECONDS,
            )
            true
        } catch (_: RuntimeException) {
            armed.set(false)
            false
        }
    }

    fun disarm() {
        if (armed.compareAndSet(true, false)) future?.cancel(false)
    }

    override fun close() = disarm()
}
