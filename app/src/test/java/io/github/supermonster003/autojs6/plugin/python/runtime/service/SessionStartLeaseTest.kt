package io.github.supermonster003.autojs6.plugin.python.runtime.service

import java.util.concurrent.Executors
import java.util.concurrent.TimeUnit
import java.util.concurrent.atomic.AtomicInteger
import org.junit.Assert.assertEquals
import org.junit.Assert.assertFalse
import org.junit.Assert.assertTrue
import org.junit.Test

class SessionStartLeaseTest {
    @Test
    fun expiresExactlyOnce() {
        val scheduler = Executors.newSingleThreadScheduledExecutor()
        try {
            val expirations = AtomicInteger()
            val lease = SessionStartLease(scheduler, 1L, expirations::incrementAndGet)
            assertTrue(lease.arm())
            assertFalse(lease.arm())
            scheduler.shutdown()
            assertTrue(scheduler.awaitTermination(5L, TimeUnit.SECONDS))
            assertEquals(1, expirations.get())
        } finally {
            scheduler.shutdownNow()
        }
    }

    @Test
    fun disarmPreventsExpiry() {
        val scheduler = Executors.newSingleThreadScheduledExecutor()
        try {
            val expirations = AtomicInteger()
            val lease = SessionStartLease(scheduler, 50L, expirations::incrementAndGet)
            assertTrue(lease.arm())
            lease.disarm()
            scheduler.shutdown()
            assertTrue(scheduler.awaitTermination(5L, TimeUnit.SECONDS))
            assertEquals(0, expirations.get())
        } finally {
            scheduler.shutdownNow()
        }
    }
}
