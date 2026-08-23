package io.github.supermonster003.autojs6.plugin.python.runtime

import io.github.supermonster003.autojs6.plugin.python.runtime.BuildConfig
import org.autojs.plugin.python.runtime.api.PythonCancellationMode
import org.autojs.plugin.python.runtime.api.PythonImplementation
import org.autojs.plugin.python.runtime.api.PythonIsolationMode
import org.autojs.plugin.python.runtime.api.PythonProtocolVersion
import org.autojs.plugin.python.runtime.api.PythonRuntimeCapabilities
import org.autojs.plugin.python.runtime.api.PythonRuntimeContract
import org.autojs.plugin.python.runtime.api.PythonRuntimeInfo
import org.autojs.plugin.python.runtime.api.PythonRuntimeResourceLimits
import org.autojs.plugin.python.runtime.api.PythonRuntimeValidation

internal object PythonRuntimeMetadata {
    const val PROVIDER_ID = "org.autojs.python.runtime.cpython"
    const val PYTHON_VERSION = "3.13.9"
    const val HOST_PACKAGE_NAME = "org.autojs.autojs6"
    const val FIRST_OUTPUT_SEQUENCE = 1L

    val protocolMinVersion = PythonProtocolVersion(
        PythonRuntimeContract.PROTOCOL_MAJOR,
        0,
    )

    val protocolVersion = PythonProtocolVersion(
        PythonRuntimeContract.PROTOCOL_MAJOR,
        PythonRuntimeContract.PROTOCOL_MINOR,
    )

    val runtimeInfo: PythonRuntimeInfo by lazy {
        PythonRuntimeInfo(
            protocolMin = protocolMinVersion,
            protocolMax = protocolVersion,
            providerId = PROVIDER_ID,
            providerVersionName = BuildConfig.VERSION_NAME,
            providerVersionCode = BuildConfig.VERSION_CODE.toLong(),
            implementation = PythonImplementation.CPYTHON,
            pythonVersion = PYTHON_VERSION,
            isolationMode = PythonIsolationMode.DEDICATED_PLUGIN_PROCESS,
            minHostVersionCode = 5275L,
        ).also(PythonRuntimeValidation::validateRuntimeInfo)
    }

    val capabilities: PythonRuntimeCapabilities by lazy {
        PythonRuntimeCapabilities(
            implementation = PythonImplementation.CPYTHON,
            pythonVersion = PYTHON_VERSION,
            supportedAbis = listOf("arm64-v8a", "x86_64"),
            supportsWorkspaceArchive = true,
            supportsStdinSnapshot = true,
            supportsStructuredTraceback = true,
            supportsCooperativeCancellation = false,
            cancellationMode = PythonCancellationMode.PROCESS_RESTART_ONLY,
            supportsHostCapabilitySnapshot = true,
            supportsModuleEntry = true,
            supportsInteractiveInput = true,
            supportsStructuredJsonResult = true,
            supportsOutputArtifacts = true,
            supportsHostCapabilityBroker = true,
            limits = PythonRuntimeResourceLimits(
                maxSourceBytes = 4L * 1024L * 1024L,
                maxWorkspaceArchiveBytes = 16L * 1024L * 1024L,
                maxWorkspaceEntries = 1024,
                maxWorkspaceUncompressedBytes = 32L * 1024L * 1024L,
                maxStdinBytes = 1L * 1024L * 1024L,
                maxOutputBytes = 16L * 1024L * 1024L,
                maxOutputChunkBytes = 16 * 1024,
                maxOutputChunks = 16_384L,
                maxOutstandingOutputCredits = PythonRuntimeContract.MAX_OUTSTANDING_OUTPUT_CREDITS,
                maxTimeoutMillis = 30L * 60L * 1_000L,
                maxConcurrentSessions = 1,
                maxHostCapabilitySnapshotBytes = PythonRuntimeContract.MAX_HOST_CAPABILITY_SNAPSHOT_BYTES,
                maxInputPromptBytes = 4 * 1024,
                maxInputReplyBytes = 64 * 1024,
                maxInputPrompts = 128,
                maxInputWaitMillis = 60_000L,
                maxStructuredJsonBytes = 64 * 1024,
                maxOutputArtifacts = 16,
                maxOutputArtifactPathBytes = 1024,
                maxOutputArtifactBytes = 4L * 1024L * 1024L,
                maxTotalOutputArtifactBytes = 8L * 1024L * 1024L,
            ),
        ).also { PythonRuntimeValidation.validateCapabilitiesAgainstInfo(it, runtimeInfo) }
    }
}
