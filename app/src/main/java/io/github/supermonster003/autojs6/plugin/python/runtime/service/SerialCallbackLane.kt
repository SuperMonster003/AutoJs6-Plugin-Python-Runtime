package io.github.supermonster003.autojs6.plugin.python.runtime.service

import io.github.supermonster003.autojs6.plugin.python.runtime.process.CallbackDrain
import java.io.Closeable
import java.util.concurrent.ArrayBlockingQueue
import java.util.concurrent.CountDownLatch
import java.util.concurrent.RejectedExecutionException
import java.util.concurrent.ThreadPoolExecutor
import java.util.concurrent.TimeUnit
import java.util.concurrent.atomic.AtomicReference

internal class SerialCallbackLane : Closeable, CallbackDrain {
    private val executor = ThreadPoolExecutor(
        1,
        1,
        0L,
        TimeUnit.MILLISECONDS,
        ArrayBlockingQueue(MAX_PENDING_CALLBACKS),
        { runnable -> Thread(runnable, "python-runtime-callback").apply { isDaemon = true } },
        ThreadPoolExecutor.AbortPolicy(),
    )

    fun dispatch(callback: () -> Unit, onFailure: (Throwable) -> Unit) {
        try {
            executor.execute { runCatching(callback).onFailure(onFailure) }
        } catch (error: RejectedExecutionException) {
            onFailure(error)
        }
    }

    fun dispatchAndWait(callback: () -> Unit) {
        val done = CountDownLatch(1)
        val failure = AtomicReference<Throwable?>()
        try {
            executor.execute {
                try {
                    callback()
                } catch (error: Throwable) {
                    failure.set(error)
                } finally {
                    done.countDown()
                }
            }
        } catch (error: RejectedExecutionException) {
            throw error
        }
        done.await()
        failure.get()?.let { throw it }
    }

    /**
     * Enqueues [callback] after every callback already accepted by this lane.
     *
     * This never waits for the lane, so it is safe to call from a Binder thread. A `false`
     * result means no drain acknowledgement can be established and the caller must retain its
     * bounded fallback.
    */
    override fun dispatchWhenDrained(callback: () -> Unit): Boolean = try {
        executor.execute { callback() }
        true
    } catch (_: RejectedExecutionException) {
        false
    }

    override fun close() {
        executor.shutdownNow()
    }

    private companion object {
        const val MAX_PENDING_CALLBACKS = 16
    }
}
