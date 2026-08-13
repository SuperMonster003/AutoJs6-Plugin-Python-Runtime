package io.github.supermonster003.autojs6.plugin.python.runtime.security

import android.content.Context
import android.content.pm.PackageInfo
import android.content.pm.PackageManager
import android.os.Binder
import android.os.Build
import io.github.supermonster003.autojs6.plugin.python.runtime.PythonRuntimeMetadata
import java.security.MessageDigest

internal class HostCallerVerifier(context: Context) {
    private val packageManager = context.applicationContext.packageManager
    private val providerPackageName = context.applicationContext.packageName

    fun enforceAllowedCaller(): Int = Binder.getCallingUid().also(::enforceAllowedUid)

    fun enforceSessionOwner(expectedUid: Int) {
        val callingUid = Binder.getCallingUid()
        if (callingUid != expectedUid) throw SecurityException("Python session owner changed")
        enforceAllowedUid(callingUid)
    }

    private fun enforceAllowedUid(callingUid: Int) {
        val hostPackage = PythonRuntimeMetadata.HOST_PACKAGE_NAME
        val installedUid = try {
            packageManager.getApplicationInfo(hostPackage, 0).uid
        } catch (_: PackageManager.NameNotFoundException) {
            null
        }
        val packagesForUid = packageManager.getPackagesForUid(callingUid)?.toSet().orEmpty()
        val providerSigners = currentSignerDigests(providerPackageName)
        val hostSigners = currentSignerDigests(hostPackage)
        val hostVersionCode = installedVersionCode(hostPackage)
        if (
            installedUid == null ||
            callingUid != installedUid ||
            hostPackage !in packagesForUid ||
            !HostVersionPolicy.isAllowed(hostVersionCode, PythonRuntimeMetadata.runtimeInfo.minHostVersionCode) ||
            providerSigners.isEmpty() ||
            providerSigners != hostSigners
        ) {
            throw SecurityException("Caller is not the installed same-signer AutoJs6 host")
        }
    }

    @Suppress("DEPRECATION")
    private fun installedVersionCode(packageName: String): Long? = try {
        val packageInfo = if (Build.VERSION.SDK_INT >= 33) {
            packageManager.getPackageInfo(packageName, PackageManager.PackageInfoFlags.of(0L))
        } else {
            packageManager.getPackageInfo(packageName, 0)
        }
        if (Build.VERSION.SDK_INT >= 28) packageInfo.longVersionCode else packageInfo.versionCode.toLong()
    } catch (_: PackageManager.NameNotFoundException) {
        null
    }

    @Suppress("DEPRECATION")
    private fun currentSignerDigests(packageName: String): Set<String> {
        val packageInfo: PackageInfo = try {
            if (Build.VERSION.SDK_INT >= 33) {
                packageManager.getPackageInfo(
                    packageName,
                    PackageManager.PackageInfoFlags.of(PackageManager.GET_SIGNING_CERTIFICATES.toLong()),
                )
            } else if (Build.VERSION.SDK_INT >= 28) {
                packageManager.getPackageInfo(packageName, PackageManager.GET_SIGNING_CERTIFICATES)
            } else {
                packageManager.getPackageInfo(packageName, PackageManager.GET_SIGNATURES)
            }
        } catch (_: PackageManager.NameNotFoundException) {
            return emptySet()
        }
        val signers = if (Build.VERSION.SDK_INT >= 28) {
            packageInfo.signingInfo?.apkContentsSigners.orEmpty()
        } else {
            packageInfo.signatures.orEmpty()
        }
        return signers.mapTo(linkedSetOf()) { signature ->
            MessageDigest.getInstance("SHA-256")
                .digest(signature.toByteArray())
                .joinToString(separator = "") { byte -> "%02x".format(byte.toInt() and 0xff) }
        }
    }
}

internal object HostVersionPolicy {
    fun isAllowed(installedVersionCode: Long?, minimumVersionCode: Long?): Boolean =
        installedVersionCode != null &&
            minimumVersionCode != null &&
            minimumVersionCode > 0L &&
            installedVersionCode >= minimumVersionCode
}
