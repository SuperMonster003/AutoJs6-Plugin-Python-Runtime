package io.github.supermonster003.autojs6.plugin.python.runtime.process

import io.github.supermonster003.autojs6.plugin.python.runtime.service.SerialCallbackLane
import io.github.supermonster003.autojs6.plugin.python.runtime.service.SingleActiveSessionGate
import java.util.Collections
import java.util.concurrent.CountDownLatch
import java.util.concurrent.Executors
import java.util.concurrent.TimeUnit
import java.util.concurrent.atomic.AtomicInteger
import org.junit.Assert.assertEquals
import org.junit.Assert.assertFalse
import org.junit.Assert.assertTrue
import org.junit.Test

class ProcessRetirementTest {
    @Test
    fun callbackDrainAcknowledgementPrecedesProcessKill() {
        val scheduler = Executors.newSingleThreadScheduledExecutor()
        val callbackLane = SerialCallbackLane()
        val gate = SingleActiveSessionGate<Any>()
        val active = Any()
        val callbackEntered = CountDownLatch(1)
        val releaseCallback = CountDownLatch(1)
        val killed = CountDownLatch(1)
        val order = Collections.synchronizedList(mutableListOf<String>())
        val retirement = ProcessRetirement(
            scheduler = scheduler,
            callbackDrain = callbackLane,
            markGenerationRetiring = { gate.markRetiring() },
            killRuntimeProcess = {
                order += "kill"
                killed.countDown()
            },
            callbackDrainTimeoutMillis = 5_000L,
        )
        try {
            assertTrue(gate.tryAcquire(active))
            callbackLane.dispatch(
                callback = {
                    callbackEntered.countDown()
                    releaseCallback.await()
                    order += "terminal"
                },
                onFailure = { throw AssertionError("Terminal callback failed", it) },
            )
            assertTrue("Terminal callback did not enter", callbackEntered.await(5, TimeUnit.SECONDS))

            retirement.retireAfterCallbackDrain()

            assertTrue(retirement.isRetiring())
            assertTrue(gate.isRetiring())
            assertFalse("RETIRING generation admitted a new session", gate.tryAcquire(Any()))
            assertFalse("Process died before callback drain", killed.await(100, TimeUnit.MILLISECONDS))

            releaseCallback.countDown()
            assertTrue("Process was not retired after callback drain", killed.await(5, TimeUnit.SECONDS))
            assertEquals(listOf("terminal", "kill"), order.toList())
        } finally {
            releaseCallback.countDown()
            callbackLane.close()
            scheduler.shutdownNow()
        }
    }

    @Test
    fun boundedFallbackKillsWhenCallbackLaneCannotDrain() {
        val scheduler = Executors.newSingleThreadScheduledExecutor()
        val callbackLane = SerialCallbackLane()
        val callbackEntered = CountDownLatch(1)
        val releaseCallback = CountDownLatch(1)
        val killed = CountDownLatch(1)
        val laneDrainedAfterRelease = CountDownLatch(1)
        val killCount = AtomicInteger()
        val retirement = ProcessRetirement(
            scheduler = scheduler,
            callbackDrain = callbackLane,
            markGenerationRetiring = {},
            killRuntimeProcess = {
                killCount.incrementAndGet()
                killed.countDown()
            },
            callbackDrainTimeoutMillis = 50L,
        )
        try {
            callbackLane.dispatch(
                callback = {
                    callbackEntered.countDown()
                    releaseCallback.await()
                },
                onFailure = { throw AssertionError("Blocking callback failed", it) },
            )
            assertTrue("Blocking callback did not enter", callbackEntered.await(5, TimeUnit.SECONDS))

            retirement.retireAfterCallbackDrain()

            assertTrue("Bounded fallback did not retire process", killed.await(5, TimeUnit.SECONDS))
            releaseCallback.countDown()
            assertTrue(callbackLane.dispatchWhenDrained { laneDrainedAfterRelease.countDown() })
            assertTrue("Callback lane did not drain after release", laneDrainedAfterRelease.await(5, TimeUnit.SECONDS))
            assertEquals("Drain acknowledgement killed more than once", 1, killCount.get())
            assertTrue(retirement.hasTriggeredKill())
        } finally {
            releaseCallback.countDown()
            callbackLane.close()
            scheduler.shutdownNow()
        }
    }

    @Test
    fun immediateAndDrainRetirementRemainExactlyOnce() {
        val scheduler = Executors.newSingleThreadScheduledExecutor()
        val callbackLane = SerialCallbackLane()
        val killCount = AtomicInteger()
        val retirement = ProcessRetirement(
            scheduler = scheduler,
            callbackDrain = callbackLane,
            markGenerationRetiring = {},
            killRuntimeProcess = { killCount.incrementAndGet() },
            callbackDrainTimeoutMillis = 5_000L,
        )
        try {
            retirement.retireNow()
            retirement.retireAfterCallbackDrain()
            retirement.retireNow()

            assertEquals(1, killCount.get())
        } finally {
            callbackLane.close()
            scheduler.shutdownNow()
        }
    }
}
