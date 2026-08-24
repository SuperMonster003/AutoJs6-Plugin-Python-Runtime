package io.github.supermonster003.autojs6.plugin.python.runtime.service

import org.autojs.plugin.python.runtime.api.PythonRequestId
import org.junit.Assert.assertEquals
import org.junit.Assert.assertThrows
import org.junit.Test

class PythonHeartbeatPolicyTest {
    @Test
    fun heartbeatsStartAtOneAndKeepMonotonicElapsedTime() {
        val policy = PythonHeartbeatPolicy(requestIdForTest(), 1_000L)

        val first = policy.next(1_015L)
        val second = policy.next(1_015L)
        val third = policy.next(1_030L)

        assertEquals(1L, first.sequence)
        assertEquals(2L, second.sequence)
        assertEquals(3L, third.sequence)
        assertEquals(15L, first.elapsedMillis)
        assertEquals(15L, second.elapsedMillis)
        assertEquals(30L, third.elapsedMillis)
    }

    @Test
    fun backwardsClockFailsClosedWithoutPublishingAnotherHeartbeat() {
        val policy = PythonHeartbeatPolicy(requestIdForTest(), 10L)
        policy.next(20L)

        assertThrows(IllegalArgumentException::class.java) { policy.next(19L) }
        assertEquals(2L, policy.next(20L).sequence)
    }
}

private fun requestIdForTest() = PythonRequestId.fromBytes(ByteArray(16) { 7 })
