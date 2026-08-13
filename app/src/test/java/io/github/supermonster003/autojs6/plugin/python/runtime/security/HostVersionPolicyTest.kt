package io.github.supermonster003.autojs6.plugin.python.runtime.security

import org.junit.Assert.assertFalse
import org.junit.Assert.assertTrue
import org.junit.Test

class HostVersionPolicyTest {
    @Test
    fun acceptsOnlyInstalledHostAtOrAboveFloor() {
        assertFalse(HostVersionPolicy.isAllowed(null, 5275L))
        assertFalse(HostVersionPolicy.isAllowed(5274L, 5275L))
        assertTrue(HostVersionPolicy.isAllowed(5275L, 5275L))
        assertTrue(HostVersionPolicy.isAllowed(6000L, 5275L))
    }

    @Test
    fun rejectsInvalidCompatibilityFloor() {
        assertFalse(HostVersionPolicy.isAllowed(5275L, 0L))
        assertFalse(HostVersionPolicy.isAllowed(5275L, -1L))
        assertFalse(HostVersionPolicy.isAllowed(5275L, null))
    }
}
