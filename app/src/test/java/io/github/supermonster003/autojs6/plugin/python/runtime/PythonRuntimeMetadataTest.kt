package io.github.supermonster003.autojs6.plugin.python.runtime

import org.autojs.plugin.python.runtime.api.PythonCancellationMode
import org.autojs.plugin.python.runtime.api.PythonImplementation
import org.autojs.plugin.python.runtime.api.PythonIsolationMode
import org.autojs.plugin.python.runtime.api.PythonProtocolVersion
import org.autojs.plugin.python.runtime.api.PythonRuntimeCodec
import org.autojs.plugin.python.runtime.api.PythonRuntimeContract
import org.autojs.plugin.python.runtime.api.PythonRuntimeResourceLimits
import org.junit.Assert.assertEquals
import org.junit.Assert.assertFalse
import org.junit.Assert.assertNull
import org.junit.Assert.assertTrue
import org.junit.Test

class PythonRuntimeMetadataTest {
    @Test
    fun officialIndexIdentityIsExactAndBuildDeclared() {
        assertEquals("python-runtime", BuildConfig.PLUGIN_ID)
        assertEquals("python", BuildConfig.PLUGIN_ENGINE)
        assertEquals("cpython-3.13", BuildConfig.PLUGIN_VARIANT)
    }

    @Test
    fun runtimeInfoAdvertisesExactPinnedIdentityAndIsolation() {
        val info = PythonRuntimeMetadata.runtimeInfo
        val protocolMax = PythonProtocolVersion(
            PythonRuntimeContract.PROTOCOL_MAJOR,
            PythonRuntimeContract.PROTOCOL_MINOR,
        )

        assertEquals(PythonProtocolVersion(PythonRuntimeContract.PROTOCOL_MAJOR, 0), info.protocolMin)
        assertEquals(protocolMax, info.protocolMax)
        assertEquals("org.autojs.python.runtime.cpython", info.providerId)
        assertEquals(BuildConfig.VERSION_NAME, info.providerVersionName)
        assertEquals(BuildConfig.VERSION_CODE.toLong(), info.providerVersionCode)
        assertEquals(PythonImplementation.CPYTHON, info.implementation)
        assertEquals("3.13.9", info.pythonVersion)
        assertEquals(PythonIsolationMode.DEDICATED_PLUGIN_PROCESS, info.isolationMode)
        assertEquals(5_275L, info.minHostVersionCode)
        assertNull(info.maxHostVersionCode)
    }

    @Test
    fun capabilitiesAdvertiseExactR5SnapshotSurfaceAndLimits() {
        val capabilities = PythonRuntimeMetadata.capabilities

        assertEquals(PythonImplementation.CPYTHON, capabilities.implementation)
        assertEquals("3.13.9", capabilities.pythonVersion)
        assertEquals(listOf("arm64-v8a", "x86_64"), capabilities.supportedAbis)
        assertTrue(capabilities.supportsWorkspaceArchive)
        assertTrue(capabilities.supportsStdinSnapshot)
        assertTrue(capabilities.supportsStructuredTraceback)
        assertFalse(capabilities.supportsCooperativeCancellation)
        assertTrue(capabilities.supportsHostCapabilitySnapshot)
        assertEquals(PythonCancellationMode.PROCESS_RESTART_ONLY, capabilities.cancellationMode)
        assertEquals(
            PythonRuntimeResourceLimits(
                maxSourceBytes = 4L * 1024L * 1024L,
                maxWorkspaceArchiveBytes = 16L * 1024L * 1024L,
                maxWorkspaceEntries = 1024,
                maxWorkspaceUncompressedBytes = 32L * 1024L * 1024L,
                maxStdinBytes = 1L * 1024L * 1024L,
                maxOutputBytes = 4L * 1024L * 1024L,
                maxOutputChunkBytes = 16 * 1024,
                maxOutputChunks = 4096L,
                maxOutstandingOutputCredits = PythonRuntimeContract.MAX_OUTSTANDING_OUTPUT_CREDITS,
                maxTimeoutMillis = 60_000L,
                maxConcurrentSessions = 1,
                maxHostCapabilitySnapshotBytes = PythonRuntimeContract.MAX_HOST_CAPABILITY_SNAPSHOT_BYTES,
            ),
            capabilities.limits,
        )
    }

    @Test
    fun metadataRoundTripsThroughTaggedWireWithoutDrift() {
        val info = PythonRuntimeMetadata.runtimeInfo
        val capabilities = PythonRuntimeMetadata.capabilities

        assertEquals(info, PythonRuntimeCodec.decodeRuntimeInfo(PythonRuntimeCodec.encodeRuntimeInfo(info)))
        assertEquals(
            capabilities,
            PythonRuntimeCodec.decodeCapabilities(PythonRuntimeCodec.encodeCapabilities(capabilities)),
        )
    }
}
