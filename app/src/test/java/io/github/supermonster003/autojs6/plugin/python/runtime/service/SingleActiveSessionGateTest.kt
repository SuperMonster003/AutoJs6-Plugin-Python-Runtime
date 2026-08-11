package io.github.supermonster003.autojs6.plugin.python.runtime.service

import org.junit.Assert.assertFalse
import org.junit.Assert.assertTrue
import org.junit.Test

class SingleActiveSessionGateTest {
    @Test
    fun firstSessionAcquiresAndSecondSessionIsRejected() {
        val gate = SingleActiveSessionGate<Any>()
        val first = Any()

        assertTrue(gate.tryAcquire(first))
        assertFalse(gate.tryAcquire(Any()))
    }

    @Test
    fun onlyOwningSessionCanRelease() {
        val gate = SingleActiveSessionGate<Any>()
        val owner = Any()

        assertTrue(gate.tryAcquire(owner))
        assertFalse(gate.release(Any()))
        assertFalse(gate.tryAcquire(Any()))
        assertTrue(gate.release(owner))
    }

    @Test
    fun releasedGateCanBeReacquiredExactlyOnce() {
        val gate = SingleActiveSessionGate<Any>()
        val first = Any()
        val second = Any()

        assertTrue(gate.tryAcquire(first))
        assertTrue(gate.release(first))
        assertFalse(gate.release(first))
        assertTrue(gate.tryAcquire(second))
        assertFalse(gate.tryAcquire(Any()))
    }

    @Test
    fun retiringGenerationRejectsAdmissionBeforeAndAfterActiveRelease() {
        val gate = SingleActiveSessionGate<Any>()
        val active = Any()

        assertTrue(gate.tryAcquire(active))
        assertTrue(gate.markRetiring())
        assertTrue(gate.isRetiring())
        assertFalse(gate.tryAcquire(Any()))
        assertTrue(gate.release(active))
        assertFalse(gate.tryAcquire(Any()))
        assertFalse(gate.markRetiring())
    }
}
