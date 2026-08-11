package io.github.supermonster003.autojs6.plugin.python.runtime.service

import java.util.Collections
import java.util.concurrent.CountDownLatch
import java.util.concurrent.RejectedExecutionException
import java.util.concurrent.TimeUnit
import java.util.concurrent.atomic.AtomicInteger
import java.util.concurrent.atomic.AtomicReference
import org.junit.Assert.assertEquals
import org.junit.Assert.assertFalse
import org.junit.Assert.assertSame
import org.junit.Assert.assertTrue
import org.junit.Assert.fail
import org.junit.Test

class SerialCallbackLaneTest {
    @Test
    fun callbacksRunInSubmissionOrderOnOneLane() {
        val lane = SerialCallbackLane()
        val order = Collections.synchronizedList(mutableListOf<Int>())
        val callbackThreads = Collections.synchronizedSet(mutableSetOf<String>())
        val done = CountDownLatch(3)
        try {
            repeat(3) { index ->
                lane.dispatch(
                    callback = {
                        order += index
                        callbackThreads += Thread.currentThread().name
                        done.countDown()
                    },
                    onFailure = { fail("Callback $index was rejected: $it") },
                )
            }

            assertTrue("Callbacks did not drain", done.await(5, TimeUnit.SECONDS))
            assertEquals(listOf(0, 1, 2), order.toList())
            assertEquals(setOf("python-runtime-callback"), callbackThreads.toSet())
        } finally {
            lane.close()
        }
    }

    @Test
    fun callbackFailureIsReportedExactlyOnceAndLaneRemainsUsable() {
        val lane = SerialCallbackLane()
        val marker = IllegalStateException("marker")
        val observedFailure = AtomicReference<Throwable?>()
        val failureCount = AtomicInteger()
        val failedCallbackDone = CountDownLatch(1)
        val followingCallbackDone = CountDownLatch(1)
        try {
            lane.dispatch(
                callback = { throw marker },
                onFailure = {
                    observedFailure.set(it)
                    failureCount.incrementAndGet()
                    failedCallbackDone.countDown()
                },
            )
            lane.dispatch(
                callback = { followingCallbackDone.countDown() },
                onFailure = { fail("Following callback was rejected: $it") },
            )

            assertTrue("Failure was not reported", failedCallbackDone.await(5, TimeUnit.SECONDS))
            assertTrue("Lane did not process the next callback", followingCallbackDone.await(5, TimeUnit.SECONDS))
            assertSame(marker, observedFailure.get())
            assertEquals(1, failureCount.get())
        } finally {
            lane.close()
        }
    }

    @Test
    fun dispatchAndWaitPropagatesCallbackFailure() {
        val lane = SerialCallbackLane()
        val marker = IllegalArgumentException("marker")
        try {
            try {
                lane.dispatchAndWait { throw marker }
                fail("Expected callback failure")
            } catch (error: IllegalArgumentException) {
                assertSame(marker, error)
            }
        } finally {
            lane.close()
        }
    }

    @Test
    fun dispatchAfterCloseReportsOneRejectionAndNeverRunsCallback() {
        val lane = SerialCallbackLane()
        val callbackRan = AtomicReference(false)
        val rejection = AtomicReference<Throwable?>()
        val failureCount = AtomicInteger()
        lane.close()

        lane.dispatch(
            callback = { callbackRan.set(true) },
            onFailure = {
                rejection.set(it)
                failureCount.incrementAndGet()
            },
        )

        assertFalse(callbackRan.get())
        assertTrue(rejection.get() is RejectedExecutionException)
        assertEquals(1, failureCount.get())
    }

    @Test
    fun drainAcknowledgementRunsOnlyAfterPreviouslyAcceptedCallbacksReturn() {
        val lane = SerialCallbackLane()
        val entered = CountDownLatch(1)
        val release = CountDownLatch(1)
        val drained = CountDownLatch(1)
        val order = Collections.synchronizedList(mutableListOf<String>())
        try {
            lane.dispatch(
                callback = {
                    entered.countDown()
                    release.await()
                    order += "terminal"
                },
                onFailure = { fail("Terminal callback failed: $it") },
            )
            assertTrue("Terminal callback did not enter", entered.await(5, TimeUnit.SECONDS))

            assertTrue(
                lane.dispatchWhenDrained {
                    order += "drained"
                    drained.countDown()
                },
            )
            assertFalse("Drain was acknowledged before callback return", drained.await(100, TimeUnit.MILLISECONDS))

            release.countDown()
            assertTrue("Drain was not acknowledged", drained.await(5, TimeUnit.SECONDS))
            assertEquals(listOf("terminal", "drained"), order.toList())
        } finally {
            release.countDown()
            lane.close()
        }
    }

    @Test
    fun closedLaneCannotEstablishDrainAcknowledgement() {
        val lane = SerialCallbackLane()
        val callbackRan = AtomicReference(false)
        lane.close()

        assertFalse(lane.dispatchWhenDrained { callbackRan.set(true) })
        assertFalse(callbackRan.get())
    }
}
