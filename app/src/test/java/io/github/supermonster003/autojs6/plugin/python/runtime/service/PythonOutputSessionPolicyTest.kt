package io.github.supermonster003.autojs6.plugin.python.runtime.service

import io.github.supermonster003.autojs6.plugin.python.runtime.PythonRuntimeMetadata
import org.autojs.plugin.python.runtime.api.PythonExecutionRequest
import org.autojs.plugin.python.runtime.api.PythonPayloadKind
import org.autojs.plugin.python.runtime.api.PythonPayloadReference
import org.autojs.plugin.python.runtime.api.PythonRuntimeContractException
import org.autojs.plugin.python.runtime.api.PythonRuntimeContractViolation
import org.autojs.plugin.python.runtime.api.PythonRuntimeValidation
import org.autojs.plugin.python.runtime.api.PythonSha256
import org.junit.Assert.assertEquals
import org.junit.Assert.assertFalse
import org.junit.Assert.assertTrue
import org.junit.Assert.fail
import org.junit.Test

/**
 * Pure-JVM conformance oracle for the session policy which is otherwise behind Android Binder
 * stubs. Device tests remain responsible for proving the real Binder session follows this model.
 */
class PythonOutputSessionPolicyTest {
    @Test
    fun providerMaximumOutputRequestIsAccepted() {
        val limits = PythonRuntimeMetadata.capabilities.limits

        PythonRuntimeValidation.validateRequestAgainst(
            request = request(
                maxOutputBytes = limits.maxOutputBytes,
                maxOutputChunkBytes = limits.maxOutputChunkBytes,
                maxOutputChunks = limits.maxOutputChunks,
            ),
            capabilities = PythonRuntimeMetadata.capabilities,
            negotiatedVersion = PythonRuntimeMetadata.protocolVersion,
            descriptorCount = 1,
        )
    }

    @Test
    fun requestsAboveEachProviderOutputLimitAreRejected() {
        val limits = PythonRuntimeMetadata.capabilities.limits
        val requests = listOf(
            request(
                maxOutputBytes = limits.maxOutputBytes + 1L,
                maxOutputChunkBytes = limits.maxOutputChunkBytes,
                maxOutputChunks = limits.maxOutputChunks,
            ),
            request(
                maxOutputBytes = limits.maxOutputBytes,
                maxOutputChunkBytes = limits.maxOutputChunkBytes + 1,
                maxOutputChunks = limits.maxOutputChunks,
            ),
            request(
                maxOutputBytes = limits.maxOutputBytes,
                maxOutputChunkBytes = limits.maxOutputChunkBytes,
                maxOutputChunks = limits.maxOutputChunks + 1L,
            ),
        )

        requests.forEach { candidate ->
            val error = expectContractViolation {
                PythonRuntimeValidation.validateRequestAgainst(
                    request = candidate,
                    capabilities = PythonRuntimeMetadata.capabilities,
                    negotiatedVersion = PythonRuntimeMetadata.protocolVersion,
                    descriptorCount = 1,
                )
            }
            assertEquals(PythonRuntimeContractViolation.CAPABILITY_INCOMPATIBLE, error.violation)
        }
    }

    @Test
    fun oneCreditPermitsExactlyOneChunkThenBackpressures() {
        val model = outputModel(maxBytes = 8L, maxChunks = 8L)

        assertTrue(model.grant(1))
        assertEquals(EmitEvent.EMITTED, model.emit(1))
        assertEquals(EmitEvent.BACKPRESSURED, model.emit(1))
        assertEquals(0, model.outstandingCredits)
        assertEquals(1L, model.outputBytes)
        assertEquals(1L, model.outputChunks)
    }

    @Test
    fun creditWindowRejectsZeroNegativeAndOverflowWithoutMutation() {
        val model = outputModel(maxBytes = 64L, maxChunks = 64L)
        val maximum = PythonRuntimeMetadata.capabilities.limits.maxOutstandingOutputCredits

        assertFalse(model.grant(0))
        assertFalse(model.grant(-1))
        assertTrue(model.grant(maximum))
        assertFalse(model.grant(1))
        assertEquals(maximum, model.outstandingCredits)
    }

    @Test
    fun byteQuotaProducesExactlyOneTerminalAndBlocksFurtherOutput() {
        val model = outputModel(maxBytes = 2L, maxChunks = 4L)

        assertTrue(model.grant(3))
        assertEquals(EmitEvent.EMITTED, model.emit(2))
        assertEquals(EmitEvent.QUOTA_TERMINAL, model.emit(1))
        assertEquals(EmitEvent.IGNORED_AFTER_TERMINAL, model.emit(1))
        assertEquals(Terminal.FAILURE, model.terminal)
        assertEquals(1, model.terminalCount)
        assertEquals(2L, model.outputBytes)
        assertEquals(1L, model.outputChunks)
    }

    @Test
    fun chunkQuotaProducesExactlyOneTerminalAndBlocksFurtherOutput() {
        val model = outputModel(maxBytes = 4L, maxChunks = 1L)

        assertTrue(model.grant(2))
        assertEquals(EmitEvent.EMITTED, model.emit(1))
        assertEquals(EmitEvent.QUOTA_TERMINAL, model.emit(1))
        assertEquals(EmitEvent.IGNORED_AFTER_TERMINAL, model.emit(1))
        assertEquals(Terminal.FAILURE, model.terminal)
        assertEquals(1, model.terminalCount)
        assertEquals(1L, model.outputBytes)
        assertEquals(1L, model.outputChunks)
    }

    @Test
    fun terminalArbitrationAcceptsOnlyFirstTerminal() {
        val model = outputModel(maxBytes = 1L, maxChunks = 1L)

        assertTrue(model.finish(Terminal.RESULT))
        assertFalse(model.finish(Terminal.FAILURE))
        assertFalse(model.finish(Terminal.CANCELLED))
        assertEquals(Terminal.RESULT, model.terminal)
        assertEquals(1, model.terminalCount)
        assertFalse(model.grant(1))
        assertEquals(EmitEvent.IGNORED_AFTER_TERMINAL, model.emit(1))
    }

    @Test
    fun acceptedPartialOutputPrecedesCancellationAndNothingFollows() {
        val model = outputModel(maxBytes = 4L, maxChunks = 4L)

        assertTrue(model.grant(2))
        assertEquals(EmitEvent.EMITTED, model.emit(1))
        assertTrue(model.finish(Terminal.CANCELLED))
        assertEquals(EmitEvent.IGNORED_AFTER_TERMINAL, model.emit(1))
        assertEquals(listOf("output", "terminal:CANCELLED"), model.events)
    }

    @Test
    fun acceptedPartialOutputPrecedesTimeoutFailureAndNothingFollows() {
        val model = outputModel(maxBytes = 4L, maxChunks = 4L)

        assertTrue(model.grant(2))
        assertEquals(EmitEvent.EMITTED, model.emit(1))
        assertTrue(model.finish(Terminal.FAILURE))
        assertEquals(EmitEvent.IGNORED_AFTER_TERMINAL, model.emit(1))
        assertEquals(listOf("output", "terminal:FAILURE"), model.events)
    }

    private fun request(
        maxOutputBytes: Long,
        maxOutputChunkBytes: Int,
        maxOutputChunks: Long,
    ): PythonExecutionRequest = PythonExecutionRequest(
        requestId = org.autojs.plugin.python.runtime.api.PythonRequestId.fromBytes(ByteArray(16) { 1 }),
        protocolVersion = PythonRuntimeMetadata.protocolVersion,
        entryPoint = "main.py",
        source = PythonPayloadReference(
            kind = PythonPayloadKind.SOURCE,
            descriptorIndex = 0,
            declaredLengthBytes = 1L,
            sha256 = PythonSha256.digest(byteArrayOf(0)),
        ),
        timeoutMillis = PythonRuntimeMetadata.capabilities.limits.maxTimeoutMillis,
        maxOutputBytes = maxOutputBytes,
        maxOutputChunkBytes = maxOutputChunkBytes,
        maxOutputChunks = maxOutputChunks,
    )

    private fun outputModel(maxBytes: Long, maxChunks: Long): OutputSessionModel = OutputSessionModel(
        maxCredits = PythonRuntimeMetadata.capabilities.limits.maxOutstandingOutputCredits,
        maxBytes = maxBytes,
        maxChunkBytes = PythonRuntimeMetadata.capabilities.limits.maxOutputChunkBytes,
        maxChunks = maxChunks,
    )

    private fun expectContractViolation(block: () -> Unit): PythonRuntimeContractException = try {
        block()
        fail("Expected PythonRuntimeContractException")
        throw AssertionError("unreachable")
    } catch (error: PythonRuntimeContractException) {
        error
    }

    private enum class Terminal { RESULT, FAILURE, CANCELLED }

    private enum class EmitEvent { EMITTED, BACKPRESSURED, QUOTA_TERMINAL, IGNORED_AFTER_TERMINAL }

    private class OutputSessionModel(
        private val maxCredits: Int,
        private val maxBytes: Long,
        private val maxChunkBytes: Int,
        private val maxChunks: Long,
    ) {
        var outstandingCredits: Int = 0
            private set
        var outputBytes: Long = 0L
            private set
        var outputChunks: Long = 0L
            private set
        var terminal: Terminal? = null
            private set
        var terminalCount: Int = 0
            private set
        val events = mutableListOf<String>()

        fun grant(count: Int): Boolean {
            if (terminal != null || count <= 0 || outstandingCredits > maxCredits - count) return false
            outstandingCredits += count
            return true
        }

        fun emit(sizeBytes: Int): EmitEvent {
            if (terminal != null) return EmitEvent.IGNORED_AFTER_TERMINAL
            require(sizeBytes in 1..maxChunkBytes)
            if (outstandingCredits == 0) return EmitEvent.BACKPRESSURED
            if (outputBytes > maxBytes - sizeBytes || outputChunks >= maxChunks) {
                finish(Terminal.FAILURE)
                return EmitEvent.QUOTA_TERMINAL
            }
            outstandingCredits--
            outputBytes += sizeBytes
            outputChunks++
            events += "output"
            return EmitEvent.EMITTED
        }

        fun finish(candidate: Terminal): Boolean {
            if (terminal != null) return false
            terminal = candidate
            terminalCount++
            events += "terminal:$candidate"
            return true
        }
    }
}
