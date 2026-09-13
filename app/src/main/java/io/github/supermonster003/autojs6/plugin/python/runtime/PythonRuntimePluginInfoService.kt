package io.github.supermonster003.autojs6.plugin.python.runtime

import android.app.Service
import android.content.Intent
import android.os.Bundle
import android.os.IBinder
import org.autojs.plugin.common.api.IPluginInfoProvider
import org.autojs.plugin.common.api.PluginCapabilityKeys
import org.autojs.plugin.common.api.PluginInfo

/** Plugin Center metadata endpoint. Runtime execution remains in the separate runtime service. */
class PythonRuntimePluginInfoService : Service() {

    private val binder = object : IPluginInfoProvider.Stub() {
        override fun getInfo(): PluginInfo {
            @Suppress("DEPRECATION")
            val installed = packageManager.getPackageInfo(packageName, 0)
            val info = PythonRuntimeMetadata.runtimeInfo
            val capabilities = Bundle().apply {
                info.minHostVersionCode?.let {
                    putInt(PluginCapabilityKeys.REQUIRES_HOST_VERSION, Math.toIntExact(it))
                }
                putString(CAPABILITY_PYTHON_VERSION, PythonRuntimeMetadata.PYTHON_VERSION)
                putString(CAPABILITY_PROVIDER_ID, PythonRuntimeMetadata.PROVIDER_ID)
                putInt(CAPABILITY_PROTOCOL_MAJOR_MIN, info.protocolMin.major)
                putInt(CAPABILITY_PROTOCOL_MINOR_MIN, info.protocolMin.minor)
                putInt(CAPABILITY_PROTOCOL_MAJOR_MAX, info.protocolMax.major)
                putInt(CAPABILITY_PROTOCOL_MINOR_MAX, info.protocolMax.minor)
                putString(CAPABILITY_RUNTIME_SERVICE_ACTION, RUNTIME_ACTION)
                putBoolean(CAPABILITY_TRUSTED_LOCAL_SCRIPTS_ONLY, true)
                putBoolean(CAPABILITY_SECURITY_SANDBOX, false)
            }
            return PluginInfo(
                name = getString(R.string.app_name),
                description = getString(R.string.plugin_description),
                instruction = null,
                author = getString(R.string.plugin_author),
                collaborators = null,
                versionName = installed.versionName,
                versionCode = if (android.os.Build.VERSION.SDK_INT >= 28) installed.longVersionCode else installed.versionCode.toLong(),
                versionDate = getString(R.string.plugin_version_date),
                id = BuildConfig.PLUGIN_ID,
                engine = BuildConfig.PLUGIN_ENGINE,
                variant = BuildConfig.PLUGIN_VARIANT,
                supportedAbis = PythonRuntimeMetadata.capabilities.supportedAbis.toTypedArray(),
                capabilities = capabilities,
            )
        }
    }

    override fun onBind(intent: Intent?): IBinder = binder

    private companion object {
        const val RUNTIME_ACTION = "org.autojs.plugin.python.RUNTIME"
        const val CAPABILITY_PYTHON_VERSION = "pythonVersion"
        const val CAPABILITY_PROVIDER_ID = "pythonProviderId"
        const val CAPABILITY_PROTOCOL_MAJOR_MIN = "pythonProtocolMajorMin"
        const val CAPABILITY_PROTOCOL_MINOR_MIN = "pythonProtocolMinorMin"
        const val CAPABILITY_PROTOCOL_MAJOR_MAX = "pythonProtocolMajorMax"
        const val CAPABILITY_PROTOCOL_MINOR_MAX = "pythonProtocolMinorMax"
        const val CAPABILITY_RUNTIME_SERVICE_ACTION = "pythonRuntimeServiceAction"
        const val CAPABILITY_TRUSTED_LOCAL_SCRIPTS_ONLY = "trustedLocalScriptsOnly"
        const val CAPABILITY_SECURITY_SANDBOX = "securitySandbox"
    }
}
