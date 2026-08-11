import java.security.MessageDigest
import java.util.Properties
import org.gradle.api.artifacts.dsl.LockMode
import org.gradle.api.provider.Property

plugins {
    id("org.autojs.build.utils")
    id("org.autojs.build.versions")
    id("org.autojs.build.signs")
    id("org.autojs.build.jvm-convention")
    id("com.android.application")
    id("com.chaquo.python")
}

val globalApplicationId = "io.github.supermonster003.autojs6.plugin.python.runtime"
val buildTypeDebug = "debug"
val buildTypeRelease = "release"
val supportedAbis = setOf("arm64-v8a", "x86_64")
val releaseSigningPropertyNames = setOf("storeFile", "storePassword", "keyAlias", "keyPassword")

fun File.sha256(): String {
    val digest = MessageDigest.getInstance("SHA-256")
    inputStream().buffered().use { input ->
        val buffer = ByteArray(DEFAULT_BUFFER_SIZE)
        while (true) {
            val count = input.read(buffer)
            if (count < 0) break
            digest.update(buffer, 0, count)
        }
    }
    return digest.digest().joinToString("") { "%02x".format(it) }
}

fun String.sha256Utf8(): String {
    val digest = MessageDigest.getInstance("SHA-256")
    return digest.digest(toByteArray(Charsets.UTF_8)).joinToString("") { "%02x".format(it) }
}

fun Properties.requiredValue(key: String): String =
    getProperty(key)?.trim()?.takeIf(String::isNotEmpty)
        ?: error("Missing required lock value: $key")

fun File.loadUniqueLock(): Properties {
    val lock = Properties()
    useLines(Charsets.UTF_8) { lines ->
        lines.forEachIndexed { index, line ->
            val trimmed = line.trim()
            if (trimmed.isEmpty() || trimmed.startsWith('#') || trimmed.startsWith('!')) {
                return@forEachIndexed
            }
            val separator = trimmed.indexOf('=')
            require(separator > 0) { "Malformed lock line ${index + 1} in $name" }
            val key = trimmed.substring(0, separator).trim()
            val value = trimmed.substring(separator + 1).trim()
            require(!lock.containsKey(key)) { "Duplicate lock key in $name: $key" }
            lock.setProperty(key, value)
        }
    }
    return lock
}

val sha256Pattern = Regex("[0-9a-f]{64}")

val releaseIdentityLockFile = rootProject.file("locks/release-identity.lock")
require(releaseIdentityLockFile.isFile) {
    "Missing release identity lock: ${releaseIdentityLockFile.relativeTo(rootProject.projectDir)}"
}
val releaseIdentityLock = releaseIdentityLockFile.loadUniqueLock()
val expectedReleaseIdentity = mapOf(
    "format" to "1",
    "host.package" to "org.autojs.autojs6",
    "plugin.package" to "io.github.supermonster003.autojs6.plugin.python.runtime",
    "release.keystore.sha256" to "0d6b79e4d4efe77829dbcc2e21096931ba7b0349df82f3b58c3e9d24e84f1df0",
    "release.certificate.sha256" to "31a681fcfffb3e428420cae280ded89292b12a3b0f59e19b7a73e32a8ae4c213",
)
require(releaseIdentityLock.stringPropertyNames() == expectedReleaseIdentity.keys) {
    "Release identity lock contains missing or unexpected keys"
}
expectedReleaseIdentity.forEach { (key, expected) ->
    require(releaseIdentityLock.requiredValue(key) == expected) {
        "Release identity lock mismatch for $key"
    }
}
require(globalApplicationId == releaseIdentityLock.requiredValue("plugin.package")) {
    "Plugin application ID differs from the release identity lock"
}
val lockedReleaseKeystoreSha256 = releaseIdentityLock.requiredValue("release.keystore.sha256")

val wrapperLockFile = rootProject.file("locks/gradle-wrapper.lock")
require(wrapperLockFile.isFile) {
    "Missing Gradle wrapper lock: ${wrapperLockFile.relativeTo(rootProject.projectDir)}"
}
val wrapperLock = wrapperLockFile.loadUniqueLock()
val wrapperPropertiesFile = rootProject.file("gradle/wrapper/gradle-wrapper.properties")
val wrapperJarFile = rootProject.file("gradle/wrapper/gradle-wrapper.jar")
require(wrapperPropertiesFile.isFile && wrapperJarFile.isFile) {
    "Gradle wrapper properties or JAR is missing"
}
val wrapperProperties = Properties().apply {
    wrapperPropertiesFile.inputStream().use(::load)
}
val expectedWrapperDistribution = mapOf(
    "format" to "1",
    "distribution.version" to "9.5.0",
    "distribution.url" to "https://services.gradle.org/distributions/gradle-9.5.0-bin.zip",
    "distribution.sha256" to "553c78f50dafcd54d65b9a444649057857469edf836431389695608536d6b746",
)
expectedWrapperDistribution.forEach { (key, expected) ->
    require(wrapperLock.requiredValue(key) == expected) {
        "Gradle wrapper lock mismatch for $key"
    }
}
require(wrapperProperties.requiredValue("distributionUrl") == wrapperLock.requiredValue("distribution.url")) {
    "Gradle wrapper distribution URL differs from the provenance lock"
}
require(wrapperProperties.requiredValue("distributionSha256Sum") == wrapperLock.requiredValue("distribution.sha256")) {
    "Gradle wrapper distribution SHA-256 differs from the provenance lock"
}
val wrapperState = wrapperLock.requiredValue("wrapper.jar.state")
val wrapperExpectedSha256 = wrapperLock.requiredValue("wrapper.jar.expected.sha256").lowercase()
val wrapperExpectedProvenance = wrapperLock.requiredValue("wrapper.jar.expected.provenance")
val wrapperObservedSha256 = wrapperLock.requiredValue("wrapper.jar.observed.sha256").lowercase()
val wrapperObservedProvenance = wrapperLock.requiredValue("wrapper.jar.observed.provenance")
val wrapperBlocker = wrapperLock.requiredValue("wrapper.jar.blocker")
val expectedWrapperLockKeys = expectedWrapperDistribution.keys + setOf(
    "wrapper.jar.state",
    "wrapper.jar.expected.sha256",
    "wrapper.jar.expected.provenance",
    "wrapper.jar.observed.sha256",
    "wrapper.jar.observed.provenance",
    "wrapper.jar.source.entry",
    "wrapper.jar.source.container.sha256",
    "wrapper.jar.blocker",
)
require(wrapperLock.stringPropertyNames() == expectedWrapperLockKeys) {
    "Gradle wrapper lock contains missing or unexpected keys"
}
val wrapperActualSha256 = wrapperJarFile.sha256()
require(sha256Pattern.matches(wrapperObservedSha256) && wrapperObservedSha256 == wrapperActualSha256) {
    "Checked-in Gradle wrapper JAR differs from its observed provenance record"
}
require(wrapperState == "READY") {
    "Gradle wrapper provenance is BLOCKED: $wrapperBlocker ($wrapperObservedProvenance)"
}
require(sha256Pattern.matches(wrapperExpectedSha256) && wrapperExpectedSha256 == wrapperActualSha256) {
    "Gradle wrapper JAR does not match the audited expected SHA-256"
}
require(wrapperExpectedProvenance == "OFFICIAL_GRADLE_9_5_0_DISTRIBUTION_EMBEDDED_WRAPPER") {
    "Gradle wrapper expected provenance is not the pinned official 9.5.0 distribution"
}
require(wrapperObservedProvenance == wrapperExpectedProvenance && wrapperBlocker == "NONE") {
    "Gradle wrapper provenance has not been promoted cleanly"
}
require(
    wrapperLock.requiredValue("wrapper.jar.source.entry") ==
        "gradle-9.5.0/lib/plugins/gradle-wrapper-main-9.5.0.jar!/gradle-wrapper.jar" &&
        wrapperLock.requiredValue("wrapper.jar.source.container.sha256") ==
        "11954fe51c5f8d56321f694ebb2aec206c3871eab57e0bef4465b9c281003982",
) {
    "Gradle wrapper source-container provenance drifted"
}

val hostApiLockFile = rootProject.file("locks/host-api-aars.lock")
require(hostApiLockFile.isFile) {
    "Missing host API lock: ${hostApiLockFile.relativeTo(rootProject.projectDir)}"
}
val hostApiLockText = hostApiLockFile.readText(Charsets.UTF_8)
val hostApiLock = hostApiLockFile.loadUniqueLock()
val hostApiIds = listOf("common-plugin-api", "protocol-wire-api", "python-runtime-api")
val expectedHostApiLockKeys = setOf("format") + hostApiIds.flatMap { id ->
    listOf("$id.file", "$id.sha256")
}
require(hostApiLock.stringPropertyNames() == expectedHostApiLockKeys) {
    "Host API AAR lock must contain exactly the three release AAR file/SHA-256 pairs"
}
require(hostApiLock.requiredValue("format") == "1") {
    "Unsupported host API AAR lock format"
}
val releaseHostApiProvenanceReady =
    Regex(
        "(?m)^#\\s*Host HEAD:\\s*[0-9a-fA-F]{40,64}\\s+" +
            "\\((?:clean current tree|clean source tree)\\)\\s*$",
    ).containsMatchIn(hostApiLockText) &&
        Regex(
            "(?m)^#\\s*Host source fingerprint:\\s*[0-9a-fA-F]{64}\\s*$",
        ).containsMatchIn(hostApiLockText) &&
        Regex(
            "(?m)^#\\s*Distribution manifest SHA-256:\\s*[0-9a-fA-F]{64}\\s*$",
        ).containsMatchIn(hostApiLockText) &&
        !Regex("(?im)^#\\s*Host HEAD:.*\\bdirty\\b").containsMatchIn(hostApiLockText)

val runtimeSupplyLockFile = rootProject.file("locks/python-runtime.lock")
require(runtimeSupplyLockFile.isFile) {
    "Missing runtime supply lock: ${runtimeSupplyLockFile.relativeTo(rootProject.projectDir)}"
}
val runtimeSupplyLock = runtimeSupplyLockFile.loadUniqueLock()
val expectedRuntimeSupply = mapOf(
    "format" to "2",
    "android.gradle.plugin.version" to "9.2.1",
    "chaquopy.plugin.version" to "17.0.0",
    "chaquopy.license" to "MIT",
    "chaquopy.repository" to "https://repo1.maven.org/maven2/com/chaquo/python/com.chaquo.python.gradle.plugin/17.0.0/",
    "python.version.requested" to "3.13",
    "python.version.expected" to "3.13.9",
    "python.license" to "PSF-2.0",
    "python.implementation" to "CPython",
    "android.minSdk" to "24",
    "android.targetSdk" to "36",
    "android.compileSdk" to "36",
    "android.abis" to "arm64-v8a,x86_64",
    "python.packages.policy" to "stdlib-only",
    "python.packages.count" to "0",
    "online.pip.allowed" to "false",
)
expectedRuntimeSupply.forEach { (key, expected) ->
    require(runtimeSupplyLock.requiredValue(key) == expected) {
        "Runtime supply lock mismatch for $key"
    }
}

val runtimeArtifactsState = runtimeSupplyLock.requiredValue("runtime.artifacts.state")
val runtimeArtifactCount = runtimeSupplyLock.requiredValue("runtime.artifacts.count").toIntOrNull()
    ?: error("runtime.artifacts.count must be an integer")
val runtimeInventorySha256 = runtimeSupplyLock.requiredValue("runtime.artifacts.inventory.sha256").lowercase()
val runtimeLockBootstrapPropertyName = "autojs.python.runtime.lock.bootstrap"
val runtimeLockBootstrapProperty = providers.gradleProperty(runtimeLockBootstrapPropertyName).orNull
require(runtimeLockBootstrapProperty == null || runtimeLockBootstrapProperty in setOf("false", "true")) {
    "$runtimeLockBootstrapPropertyName must be exactly true or false when present"
}
val runtimeLockBootstrapRequested = runtimeLockBootstrapProperty == "true"
val runtimeLockBootstrapAllowedTasks = setOf(
    ":app:assembleDebug",
    ":app:lintDebug",
    ":app:testDebugUnitTest",
)
val runtimeLockBootstrapRequestedTasks = gradle.startParameter.taskNames
val runtimeLockBootstrapHasExactTasks =
    runtimeLockBootstrapRequestedTasks.size == runtimeLockBootstrapAllowedTasks.size &&
        runtimeLockBootstrapRequestedTasks.toSet() == runtimeLockBootstrapAllowedTasks
val runtimeLockBootstrapWritesAllLocks =
    gradle.startParameter.isWriteDependencyLocks &&
        gradle.startParameter.lockedDependenciesToUpdate.isEmpty()
val runtimeLockBootstrapWritesSha256Verification =
    gradle.startParameter.writeDependencyVerifications == listOf("sha256")
val runtimeLockBootstrapHasNoExcludedTasks = gradle.startParameter.excludedTaskNames.isEmpty()
val runtimeLockBootstrapIsNotDryRun = !gradle.startParameter.isDryRun
val runtimeLockBootstrapAdmitted =
    runtimeLockBootstrapRequested &&
        runtimeLockBootstrapHasExactTasks &&
        runtimeLockBootstrapWritesAllLocks &&
        runtimeLockBootstrapWritesSha256Verification &&
        runtimeLockBootstrapHasNoExcludedTasks &&
        runtimeLockBootstrapIsNotDryRun

if (runtimeLockBootstrapRequested) {
    require(runtimeLockBootstrapHasExactTasks) {
        "Runtime lock bootstrap requires exactly these tasks: " +
            runtimeLockBootstrapAllowedTasks.sorted().joinToString(" ")
    }
    require(runtimeLockBootstrapWritesAllLocks) {
        "Runtime lock bootstrap requires --write-locks and forbids --update-locks"
    }
    require(runtimeLockBootstrapWritesSha256Verification) {
        "Runtime lock bootstrap requires exactly --write-verification-metadata sha256"
    }
    require(runtimeLockBootstrapHasNoExcludedTasks) {
        "Runtime lock bootstrap forbids excluded tasks"
    }
    require(runtimeLockBootstrapIsNotDryRun) {
        "Runtime lock bootstrap forbids --dry-run"
    }
}
val runtimeArtifactKeyPattern = Regex("runtime\\.artifact\\.\\d{3}\\.(coordinate|file|sha256)")
val runtimeArtifactNamespaceKeys = runtimeSupplyLock.stringPropertyNames()
    .filter { it.startsWith("runtime.artifact.") }
    .toSet()
require(runtimeArtifactNamespaceKeys.all(runtimeArtifactKeyPattern::matches)) {
    "Runtime artifact inventory contains an unsupported key"
}
val declaredRuntimeArtifactKeys = runtimeArtifactNamespaceKeys
val expectedRuntimeLockKeys = expectedRuntimeSupply.keys + setOf(
    "runtime.artifacts.state",
    "runtime.artifacts.count",
    "runtime.artifacts.inventory.sha256",
) + declaredRuntimeArtifactKeys
require(runtimeSupplyLock.stringPropertyNames() == expectedRuntimeLockKeys) {
    "Runtime supply lock contains missing or unexpected keys"
}

when (runtimeArtifactsState) {
    "DEFERRED" -> {
        require(runtimeArtifactCount == 0 && runtimeInventorySha256 == "deferred") {
            "DEFERRED runtime supply lock must have zero artifacts and a DEFERRED inventory"
        }
        require(declaredRuntimeArtifactKeys.isEmpty()) {
            "DEFERRED runtime supply lock must not contain candidate artifact entries"
        }
    }

    "RESOLVED" -> {
        require(runtimeArtifactCount > 0 && sha256Pattern.matches(runtimeInventorySha256)) {
            "RESOLVED runtime supply lock requires artifacts and a real inventory SHA-256"
        }
        val expectedArtifactKeys = mutableSetOf<String>()
        val artifactIdentities = mutableSetOf<String>()
        val canonicalInventory = buildString {
            repeat(runtimeArtifactCount) { index ->
                val ordinal = index.toString().padStart(3, '0')
                val prefix = "runtime.artifact.$ordinal"
                val coordinateKey = "$prefix.coordinate"
                val fileKey = "$prefix.file"
                val sha256Key = "$prefix.sha256"
                expectedArtifactKeys += setOf(coordinateKey, fileKey, sha256Key)
                val coordinate = runtimeSupplyLock.requiredValue(coordinateKey)
                val fileName = runtimeSupplyLock.requiredValue(fileKey)
                val sha256 = runtimeSupplyLock.requiredValue(sha256Key).lowercase()
                require(coordinate.none { it == '|' || it == '\n' || it == '\r' }) {
                    "Invalid runtime artifact coordinate at $ordinal"
                }
                require(fileName == File(fileName).name && '/' !in fileName && '\\' !in fileName) {
                    "Runtime artifact file must be a basename at $ordinal"
                }
                require(sha256Pattern.matches(sha256)) {
                    "Runtime artifact SHA-256 is invalid at $ordinal"
                }
                require(artifactIdentities.add("$coordinate|$fileName")) {
                    "Duplicate runtime artifact identity at $ordinal"
                }
                append(ordinal)
                append('|')
                append(coordinate)
                append('|')
                append(fileName)
                append('|')
                append(sha256)
                append('\n')
            }
        }
        require(declaredRuntimeArtifactKeys == expectedArtifactKeys) {
            "Runtime artifact inventory contains missing, extra, or non-contiguous entries"
        }
        require(canonicalInventory.sha256Utf8() == runtimeInventorySha256) {
            "Runtime artifact canonical inventory SHA-256 mismatch"
        }
    }

    else -> error("Unsupported runtime.artifacts.state: $runtimeArtifactsState")
}
require(runtimeArtifactsState == "RESOLVED" || runtimeLockBootstrapAdmitted) {
    "Runtime supply lock is DEFERRED; ordinary Gradle configuration requires audited per-artifact hashes. " +
        "The only exception is the explicit, write-only runtime lock bootstrap documented in locks/README.md"
}

fun lockedHostApiAar(id: String): File {
    val fileName = hostApiLock.getProperty("$id.file")?.trim().orEmpty()
    val expectedSha256 = hostApiLock.getProperty("$id.sha256")?.trim()?.lowercase().orEmpty()
    require(fileName.isNotEmpty() && fileName == File(fileName).name && fileName.endsWith(".aar")) {
        "Invalid $id.file in ${hostApiLockFile.name}"
    }
    require(!fileName.endsWith("-debug.aar")) {
        "Debug AARs are forbidden: $fileName"
    }
    require(sha256Pattern.matches(expectedSha256)) {
        "Replace $id.sha256 with the audited release AAR SHA-256 before Gradle configuration"
    }
    val artifact = rootProject.file("libs/$fileName")
    require(artifact.isFile) {
        "Missing locked host API AAR: ${artifact.relativeTo(rootProject.projectDir)}"
    }
    val actualSha256 = artifact.sha256()
    require(actualSha256 == expectedSha256) {
        "SHA-256 mismatch for $fileName: expected $expectedSha256, actual $actualSha256"
    }
    return artifact
}

val protocolWireApiAar = lockedHostApiAar("protocol-wire-api")
val pythonRuntimeApiAar = lockedHostApiAar("python-runtime-api")
val commonPluginApiAar = lockedHostApiAar("common-plugin-api")

val releaseSigningValues = releaseSigningPropertyNames.associateWith { key ->
    signs.properties.getProperty(key)?.trim()?.takeIf(String::isNotEmpty)
}
val releaseSigningStoreFile = releaseSigningValues.getValue("storeFile")?.let(project::file)
val releaseSigningStoreIsPinned = releaseSigningStoreFile?.let { storeFile ->
    storeFile.isFile &&
        storeFile.canRead() &&
        storeFile.sha256() == lockedReleaseKeystoreSha256
} == true
val releaseSigningReady =
    signs.isValid &&
        releaseSigningValues.values.all { it != null } &&
        releaseSigningStoreIsPinned

android {
    namespace = globalApplicationId
    compileSdk = 36

    defaultConfig {
        applicationId = globalApplicationId
        minSdk = 24
        targetSdk = 36
        versionCode = versions.appVersionCode
        versionName = versions.appVersionName

        buildConfigField("String", "PLUGIN_ID", "\"python-runtime\"")
        buildConfigField("String", "PLUGIN_ENGINE", "\"python\"")
        buildConfigField("String", "PLUGIN_VARIANT", "\"cpython-3.13\"")
        resValue("string", "plugin_id", "python-runtime")
        resValue("string", "plugin_engine", "python")
        resValue("string", "plugin_variant", "cpython-3.13")
        resValue("string", "plugin_author", "SuperMonster003")
        resValue("string", "plugin_version_date", utils.getDateString("MMM d, yyyy", "GMT+08:00"))

        ndk {
            abiFilters += supportedAbis
        }
    }

    lint {
        abortOnError = true
    }

    signingConfigs {
        if (releaseSigningReady) {
            create(buildTypeRelease) {
                storeFile = releaseSigningStoreFile
                keyPassword = releaseSigningValues.getValue("keyPassword")
                keyAlias = releaseSigningValues.getValue("keyAlias")
                storePassword = releaseSigningValues.getValue("storePassword")
            }
        }
    }

    buildTypes {
        val rules = arrayOf<Any>(
            getDefaultProguardFile("proguard-android-optimize.txt"),
            "proguard-rules.pro",
        )
        val releaseSigning = takeIf { releaseSigningReady }?.let {
            signingConfigs.getByName(buildTypeRelease)
        }
        debug {
            isMinifyEnabled = false
            proguardFiles(*rules)
            releaseSigning?.let { signingConfig = it }
        }
        release {
            isMinifyEnabled = true
            isShrinkResources = true
            proguardFiles(*rules)
            releaseSigning?.let { signingConfig = it }
        }
    }

    buildFeatures {
        aidl = true
        buildConfig = true
        resValues = true
    }

    sourceSets.named("main") {
        kotlin.directories += "src/main/java"
    }

    splits {
        abi {
            isEnable = true
            reset()
            include(*supportedAbis.toTypedArray())
            isUniversalApk = true
        }
    }

    packaging {
        jniLibs.useLegacyPackaging = false
        resources.pickFirsts.addAll(
            listOf(
                "META-INF/DEPENDENCIES",
                "META-INF/LICENSE",
                "META-INF/LICENSE.*",
                "META-INF/NOTICE",
                "META-INF/NOTICE.*",
                "META-INF/*.kotlin_module",
            ),
        )
    }

    bundle {
        language.enableSplit = false
        density.enableSplit = false
        abi.enableSplit = true
    }
}

androidComponents {
    onVariants { variant ->
        variant.outputs.forEach { output ->
            val architecture = output.filters.firstOrNull {
                it.filterType.toString() == "ABI"
            }?.identifier ?: "universal"
            val outputFileNameProperty = output.javaClass.methods.firstOrNull {
                it.name == "getOutputFileName" && it.parameterTypes.isEmpty()
            }?.invoke(output) as? Property<*>

            @Suppress("UNCHECKED_CAST")
            (outputFileNameProperty as? Property<String>)?.set(
                output.versionName.map { versionName ->
                    val normalizedVersion = versionName.replace(Regex("\\s+"), "-")
                    "${rootProject.name}-v$normalizedVersion-$architecture.apk".lowercase()
                },
            )
        }
    }
}

chaquopy {
    defaultConfig {
        version = "3.13"
    }
}

dependencies {
    implementation("org.jetbrains.kotlin:kotlin-stdlib:2.2.21")
    implementation("org.jetbrains.kotlin:kotlin-parcelize-runtime:2.2.21")
    implementation(files(commonPluginApiAar))
    implementation(files(protocolWireApiAar))
    implementation(files(pythonRuntimeApiAar))

    testImplementation(libs.junit)
}

dependencyLocking {
    lockAllConfigurations()
    lockMode = LockMode.STRICT
}

tasks.withType(JavaCompile::class.java).configureEach {
    options.encoding = "UTF-8"
}

val collectReleaseFiles by tasks.registering(Sync::class) {
    description = "Collects the three signed release APK variants"
    dependsOn("assembleRelease")
    from(layout.buildDirectory.dir("outputs/apk/release"))
    into(rootProject.layout.projectDirectory.dir("release"))
    include("${rootProject.name.lowercase()}-v${versions.appVersionName}-*.apk")
}

tasks.register<Copy>("appendDigestToReleasedFiles") {
    description = "Appends CRC32 digests to the three released APK filenames"
    dependsOn(collectReleaseFiles)
    val sourceDirectory = rootProject.file("release")
    from(sourceDirectory)
    into(rootProject.file("releases"))
    include("${rootProject.name.lowercase()}-v${versions.appVersionName}-*.apk")
    doFirst {
        val releasePrefix = "${rootProject.name.lowercase()}-v${versions.appVersionName}-"
        rootProject.file("releases").listFiles()
            .orEmpty()
            .filter { it.isFile && it.name.startsWith(releasePrefix) && it.name.endsWith(".apk") }
            .forEach { stale ->
                require(stale.delete()) { "Unable to remove stale release APK: ${stale.absolutePath}" }
            }
    }
    rename { name ->
        val stem = name.removeSuffix(".apk")
        val digest = utils.digestCRC32(sourceDirectory.resolve(name))
        "$stem-$digest.apk"
    }
    doLast {
        val outputs = rootProject.file("releases").listFiles()
            .orEmpty()
            .filter { it.isFile && it.name.endsWith(".apk") }
            .filter { it.name.startsWith("${rootProject.name.lowercase()}-v${versions.appVersionName}-") }
        require(outputs.size == 3) {
            "Expected exactly three digested release APKs for ${versions.appVersionName}"
        }
        println("Destination: ${rootProject.file("releases")}")
    }
}

fun gitOutput(vararg arguments: String): String {
    val process = ProcessBuilder(listOf("git", *arguments))
        .directory(rootProject.projectDir)
        .redirectErrorStream(true)
        .start()
    val output = process.inputStream.bufferedReader(Charsets.UTF_8).use { it.readText() }.trim()
    require(process.waitFor() == 0) {
        "Release candidate provenance requires an initialized Git HEAD"
    }
    return output
}

fun isReleaseArtifactTask(taskName: String): Boolean =
    taskName.equals("assembleRelease", ignoreCase = true) ||
        taskName.equals("bundleRelease", ignoreCase = true) ||
        taskName.equals("packageRelease", ignoreCase = true) ||
        taskName.equals("collectReleaseFiles", ignoreCase = true) ||
        taskName.equals("appendDigestToReleasedFiles", ignoreCase = true) ||
        Regex("^publish.*release.*$", RegexOption.IGNORE_CASE).matches(taskName)

gradle.taskGraph.whenReady {
    val createsReleaseArtifact = allTasks.any { task ->
        task.project == project && isReleaseArtifactTask(task.name)
    }
    if (!createsReleaseArtifact) return@whenReady

    require(releaseSigningReady) {
        "Release artifact creation requires sign.properties with storeFile, storePassword, " +
            "keyAlias, and keyPassword, plus the exact release-identity.lock keystore bytes; " +
            "unsigned release artifacts are forbidden and signer drift is forbidden"
    }
    require(releaseHostApiProvenanceReady) {
        "Release artifact creation requires a clean Host HEAD, source fingerprint, and " +
            "distribution manifest identity in locks/host-api-aars.lock"
    }
    val head = gitOutput("rev-parse", "--verify", "HEAD")
    require(Regex("[0-9a-fA-F]{40,64}").matches(head)) {
        "Release candidate provenance requires a full Git commit identity"
    }
    val commitCount = gitOutput("rev-list", "--count", "HEAD").toIntOrNull()
        ?: error("Release candidate provenance requires a numeric Git commit count")
    require(versions.appVersionCode == commitCount) {
        "VERSION_BUILD must equal the Git commit count before release artifact creation"
    }
    require(gitOutput("status", "--porcelain", "--untracked-files=all").isEmpty()) {
        "Release artifact creation requires a clean Git worktree"
    }
}

extra {
    versions.handleIfNeeded(project, "", listOf(buildTypeDebug, buildTypeRelease))
}
