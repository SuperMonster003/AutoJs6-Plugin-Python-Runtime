package io.github.supermonster003.autojs6.plugin.python.runtime.execution

import org.autojs.plugin.python.runtime.api.PythonInputEcho
import org.autojs.plugin.python.runtime.api.PythonInputReply
import org.autojs.plugin.python.runtime.api.PythonInputReplyStatus
import org.autojs.plugin.python.runtime.api.PythonRuntimeValidation
import java.util.concurrent.atomic.AtomicReference

/** Narrow execution-local bridge used only by the patched CPython built-in input function. */
internal class ChaquopyInputBridge(
    private val onInput: (String, PythonInputEcho) -> PythonInputReply,
) {
    private val failure = AtomicReference<Throwable?>()

    /** Called reflectively by the packaged Python bootstrap. */
    @Suppress("unused")
    @Synchronized
    fun request(prompt: String, echo: String): String {
        if (failure.get() != null) return CANCELLED
        return try {
            val echoPolicy = when (echo) {
                "visible" -> PythonInputEcho.VISIBLE
                "hidden" -> PythonInputEcho.HIDDEN
                else -> throw IllegalArgumentException("Python bootstrap requested an unknown input echo policy")
            }
            val reply = onInput(prompt, echoPolicy).also(PythonRuntimeValidation::validateInputReply)
            when (reply.status) {
                PythonInputReplyStatus.VALUE -> VALUE + requireNotNull(reply.value)
                PythonInputReplyStatus.EOF -> EOF
                PythonInputReplyStatus.CANCELLED -> CANCELLED
            }
        } catch (error: Throwable) {
            failure.compareAndSet(null, error)
            CANCELLED
        }
    }

    fun rethrowFailure() {
        val error = failure.get() ?: return
        when (error) {
            is InterruptedException -> {
                Thread.currentThread().interrupt()
                throw error
            }
            is PythonInputTimeoutException -> throw error
            is PythonInputLimitExceededException -> throw error
            else -> throw PythonInputDeliveryException(error)
        }
    }

    private companion object {
        const val VALUE = "\u0001"
        const val EOF = "\u0002"
        const val CANCELLED = "\u0003"
    }
}

internal class PythonInputTimeoutException : Exception("Python interactive input reply timed out")

internal class PythonInputLimitExceededException : Exception("Python interactive input exceeded its negotiated limit")

internal class PythonInputDeliveryException(cause: Throwable) :
    Exception("Python interactive input delivery failed", cause)
