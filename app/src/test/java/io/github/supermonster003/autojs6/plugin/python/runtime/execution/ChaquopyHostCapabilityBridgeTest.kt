package io.github.supermonster003.autojs6.plugin.python.runtime.execution

import org.autojs.plugin.python.runtime.api.PythonRuntimeContract
import org.junit.Assert.assertEquals
import org.junit.Assert.assertThrows
import org.junit.Assert.assertTrue
import org.junit.Test

class ChaquopyHostCapabilityBridgeTest {
    @Test
    fun forwardsStrictUtf8AndRejectsEveryCallAfterClose() {
        val requests = mutableListOf<String>()
        val bridge = ChaquopyHostCapabilityBridge { request ->
            requests += request.toString(Charsets.UTF_8)
            "{\"ok\":true}".toByteArray()
        }

        assertEquals("{\"ok\":true}", bridge.dispatch("{\"text\":\"你好\"}"))
        assertEquals(listOf("{\"text\":\"你好\"}"), requests)
        bridge.close()
        assertThrows(IllegalStateException::class.java) { bridge.dispatch("{}") }
    }

    @Test
    fun enforcesBothByteLimitsAndStrictResponseEncoding() {
        val echo = ChaquopyHostCapabilityBridge { it }
        assertThrows(IllegalArgumentException::class.java) {
            echo.dispatch("x".repeat(PythonRuntimeContract.MAX_HOST_CAPABILITY_REQUEST_BYTES + 1))
        }

        val oversized = ChaquopyHostCapabilityBridge {
            ByteArray(PythonRuntimeContract.MAX_HOST_CAPABILITY_RESPONSE_BYTES + 1)
        }
        assertThrows(IllegalArgumentException::class.java) { oversized.dispatch("{}") }

        val malformed = ChaquopyHostCapabilityBridge { byteArrayOf(0x80.toByte()) }
        assertThrows(IllegalArgumentException::class.java) { malformed.dispatch("{}") }
    }

    @Test
    fun remoteFailureClosesTheBridgePermanently() {
        var calls = 0
        val bridge = ChaquopyHostCapabilityBridge {
            calls++
            throw IllegalStateException("remote failed")
        }

        val first = assertThrows(IllegalStateException::class.java) { bridge.dispatch("{}") }
        assertTrue(first.message.orEmpty().contains("unavailable"))
        assertThrows(IllegalStateException::class.java) { bridge.dispatch("{}") }
        assertEquals(1, calls)
    }
}
