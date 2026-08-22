package io.github.supermonster003.autojs6.plugin.python.runtime.execution

import org.autojs.plugin.python.runtime.api.PythonOutputStream
import java.util.concurrent.atomic.AtomicReference

/**
 * Narrow, execution-local bridge from CPython's captured streams to the Plugin session.
 *
 * User globals never receive this object. It carries only a stream discriminator and bytes,
 * and deliberately has no Host Binder, Context, callback, or other capability surface.
 */
internal class ChaquopyOutputSink(
    private val onOutput: (BufferedOutputRecord) -> Unit,
) {
    private val failure = AtomicReference<Throwable?>()

    /** Called reflectively by the packaged Python bootstrap. */
    @Suppress("unused")
    @Synchronized
    fun emit(stream: String, payload: ByteArray): Boolean {
        if (failure.get() != null) return false
        val record = try {
            require(payload.isNotEmpty()) { "Python bootstrap emitted an empty output chunk" }
            val outputStream = when (stream) {
                "stdout" -> PythonOutputStream.STDOUT
                "stderr" -> PythonOutputStream.STDERR
                else -> throw IllegalArgumentException("Python bootstrap emitted an unknown output stream")
            }
            BufferedOutputRecord(outputStream, payload.copyOf())
        } catch (error: Throwable) {
            failure.compareAndSet(null, error)
            return false
        }
        return try {
            onOutput(record)
            true
        } catch (error: Throwable) {
            failure.compareAndSet(null, error)
            false
        }
    }

    fun rethrowFailure() {
        val error = failure.get() ?: return
        if (error is InterruptedException) {
            Thread.currentThread().interrupt()
            throw error
        }
        if (error is PythonOutputLimitExceededException) throw error
        throw PythonOutputDeliveryException(error)
    }
}

internal class PythonOutputDeliveryException(cause: Throwable) :
    Exception("Python execution-time output delivery failed", cause)

internal class PythonOutputLimitExceededException :
    Exception("Python execution-time output exceeded the negotiated limit")
