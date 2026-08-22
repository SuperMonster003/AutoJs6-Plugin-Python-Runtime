package io.github.supermonster003.autojs6.plugin.python.runtime.execution

import org.autojs.plugin.python.runtime.api.PythonOutputStream
import org.junit.Assert.assertArrayEquals
import org.junit.Assert.assertEquals
import org.junit.Assert.assertFalse
import org.junit.Assert.assertSame
import org.junit.Assert.assertTrue
import org.junit.Assert.fail
import org.junit.Test

class ChaquopyOutputSinkTest {
    @Test
    fun mapsStreamsAndCopiesPayloadBeforeDelivery() {
        val records = mutableListOf<BufferedOutputRecord>()
        val sink = ChaquopyOutputSink(records::add)
        val stdout = byteArrayOf(1, 2, 3)
        val stderr = byteArrayOf(4, 5)

        assertTrue(sink.emit("stdout", stdout))
        assertTrue(sink.emit("stderr", stderr))
        stdout.fill(9)
        stderr.fill(9)
        sink.rethrowFailure()

        assertEquals(listOf(PythonOutputStream.STDOUT, PythonOutputStream.STDERR), records.map { it.stream })
        assertArrayEquals(byteArrayOf(1, 2, 3), records[0].bytes)
        assertArrayEquals(byteArrayOf(4, 5), records[1].bytes)
    }

    @Test
    fun callbackFailureStopsFurtherOutputAndIsReportedAsDeliveryFailure() {
        val cause = IllegalStateException("callback failed")
        var calls = 0
        val sink = ChaquopyOutputSink {
            calls++
            throw cause
        }

        assertFalse(sink.emit("stdout", byteArrayOf(1)))
        assertFalse(sink.emit("stderr", byteArrayOf(2)))
        assertEquals(1, calls)
        val failure = try {
            sink.rethrowFailure()
            fail("Expected PythonOutputDeliveryException")
            throw AssertionError("unreachable")
        } catch (error: PythonOutputDeliveryException) {
            error
        }
        assertSame(cause, failure.cause)
    }

    @Test
    fun invalidStreamAndEmptyPayloadFailClosed() {
        val unknown = ChaquopyOutputSink { fail("Unexpected callback") }
        assertFalse(unknown.emit("other", byteArrayOf(1)))
        assertTrue(expectDeliveryFailure(unknown).cause is IllegalArgumentException)

        val empty = ChaquopyOutputSink { fail("Unexpected callback") }
        assertFalse(empty.emit("stdout", byteArrayOf()))
        assertTrue(expectDeliveryFailure(empty).cause is IllegalArgumentException)
    }

    @Test
    fun interruptionIsPreservedForSessionCancellationAndTimeout() {
        val interruption = InterruptedException("session stopped")
        val sink = ChaquopyOutputSink { throw interruption }

        assertFalse(sink.emit("stdout", byteArrayOf(1)))
        try {
            sink.rethrowFailure()
            fail("Expected InterruptedException")
        } catch (error: InterruptedException) {
            assertSame(interruption, error)
            assertTrue(Thread.currentThread().isInterrupted)
        } finally {
            Thread.interrupted()
        }
    }

    @Test
    fun negotiatedLimitFailureIsPreservedForTheSessionTerminal() {
        val sink = ChaquopyOutputSink { throw PythonOutputLimitExceededException() }

        assertFalse(sink.emit("stdout", byteArrayOf(1)))
        try {
            sink.rethrowFailure()
            fail("Expected PythonOutputLimitExceededException")
        } catch (_: PythonOutputLimitExceededException) {
            // Expected: the session maps this to OUTPUT_LIMIT_EXCEEDED, not INTERNAL.
        }
    }

    private fun expectDeliveryFailure(sink: ChaquopyOutputSink): PythonOutputDeliveryException = try {
        sink.rethrowFailure()
        fail("Expected PythonOutputDeliveryException")
        throw AssertionError("unreachable")
    } catch (error: PythonOutputDeliveryException) {
        error
    }
}
