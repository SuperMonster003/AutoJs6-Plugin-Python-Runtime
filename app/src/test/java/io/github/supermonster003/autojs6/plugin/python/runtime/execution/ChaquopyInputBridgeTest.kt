package io.github.supermonster003.autojs6.plugin.python.runtime.execution

import org.autojs.plugin.python.runtime.api.PythonInputEcho
import org.autojs.plugin.python.runtime.api.PythonInputReply
import org.autojs.plugin.python.runtime.api.PythonInputReplyStatus
import org.autojs.plugin.python.runtime.api.PythonPromptId
import org.autojs.plugin.python.runtime.api.PythonRequestId
import org.junit.Assert.assertEquals
import org.junit.Assert.assertThrows
import org.junit.Assert.assertTrue
import org.junit.Test
import java.util.UUID

class ChaquopyInputBridgeTest {
    @Test
    fun typedRepliesMapToPrivateBootstrapMarkersWithoutLosingEmptyValues() {
        val echoes = mutableListOf<PythonInputEcho>()
        val replies = ArrayDeque(
            listOf(
                reply(PythonInputReplyStatus.VALUE, "Ada"),
                reply(PythonInputReplyStatus.VALUE, ""),
                reply(PythonInputReplyStatus.EOF),
                reply(PythonInputReplyStatus.CANCELLED),
            ),
        )
        val bridge = ChaquopyInputBridge { _, echo ->
            echoes += echo
            replies.removeFirst()
        }

        assertEquals("\u0001Ada", bridge.request("Name: ", "visible"))
        assertEquals("\u0001", bridge.request("Empty: ", "hidden"))
        assertEquals("\u0002", bridge.request("EOF: ", "visible"))
        assertEquals("\u0003", bridge.request("Cancel: ", "visible"))
        assertEquals(
            listOf(
                PythonInputEcho.VISIBLE,
                PythonInputEcho.HIDDEN,
                PythonInputEcho.VISIBLE,
                PythonInputEcho.VISIBLE,
            ),
            echoes,
        )
        bridge.rethrowFailure()
    }

    @Test
    fun interruptionAndNegotiatedFailuresArePreservedForSessionTerminalMapping() {
        val interrupted = ChaquopyInputBridge { _, _ -> throw InterruptedException("cancelled") }
        assertEquals("\u0003", interrupted.request("", "visible"))
        assertThrows(InterruptedException::class.java) { interrupted.rethrowFailure() }
        assertTrue(Thread.interrupted())

        val timeout = ChaquopyInputBridge { _, _ -> throw PythonInputTimeoutException() }
        assertEquals("\u0003", timeout.request("", "visible"))
        assertThrows(PythonInputTimeoutException::class.java) { timeout.rethrowFailure() }

        val limit = ChaquopyInputBridge { _, _ -> throw PythonInputLimitExceededException() }
        assertEquals("\u0003", limit.request("", "visible"))
        assertThrows(PythonInputLimitExceededException::class.java) { limit.rethrowFailure() }
    }

    @Test
    fun malformedReplyUnknownEchoAndCallbackFailureFailClosed() {
        val malformed = ChaquopyInputBridge { _, _ ->
            reply(PythonInputReplyStatus.VALUE, value = null)
        }
        assertEquals("\u0003", malformed.request("", "visible"))
        assertThrows(PythonInputDeliveryException::class.java) { malformed.rethrowFailure() }

        val unknownEcho = ChaquopyInputBridge { _, _ -> reply(PythonInputReplyStatus.EOF) }
        assertEquals("\u0003", unknownEcho.request("", "unsupported"))
        assertThrows(PythonInputDeliveryException::class.java) { unknownEcho.rethrowFailure() }

        var callbackCount = 0
        val failed = ChaquopyInputBridge { _, _ ->
            callbackCount++
            throw IllegalStateException("delivery failed")
        }
        assertEquals("\u0003", failed.request("", "visible"))
        assertEquals("\u0003", failed.request("", "visible"))
        assertEquals(1, callbackCount)
        assertThrows(PythonInputDeliveryException::class.java) { failed.rethrowFailure() }
    }

    private fun reply(status: PythonInputReplyStatus, value: String? = null) = PythonInputReply(
        requestId = REQUEST_ID,
        promptId = PythonPromptId.fromLong(1),
        status = status,
        value = value,
    )

    private companion object {
        val REQUEST_ID: PythonRequestId = PythonRequestId.fromUuid(
            UUID.fromString("12345678-1234-5678-9abc-def012345678"),
        )
    }
}
