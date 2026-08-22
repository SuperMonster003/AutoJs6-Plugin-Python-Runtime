package io.github.supermonster003.autojs6.plugin.python.runtime.transport

import android.os.ParcelFileDescriptor
import android.system.ErrnoException
import android.system.Os
import android.system.OsConstants
import org.autojs.plugin.python.runtime.api.PythonEntryMode
import org.autojs.plugin.python.runtime.api.PythonPayloadReference
import org.autojs.plugin.python.runtime.api.PythonRuntimeValidation
import java.io.BufferedInputStream
import java.io.BufferedOutputStream
import java.io.Closeable
import java.io.File
import java.io.FileInputStream
import java.io.FileOutputStream
import java.io.RandomAccessFile
import java.nio.charset.StandardCharsets
import java.security.MessageDigest
import java.text.Normalizer
import java.util.Locale
import java.util.UUID
import java.util.concurrent.atomic.AtomicReference
import java.util.zip.ZipEntry
import java.util.zip.ZipInputStream

/** One request-owned, provider-private project tree. It never writes back to host storage. */
internal class WorkspaceSnapshot private constructor(
    container: File,
    val root: File,
) : Closeable {
    private val ownedContainer = AtomicReference(container)

    override fun close() {
        ownedContainer.getAndSet(null)?.let { container -> runCatching { deleteTreeNoFollow(container) } }
    }

    companion object {
        fun materialize(
            reference: PythonPayloadReference,
            descriptor: ParcelFileDescriptor,
            sourceReference: PythonPayloadReference,
            sourceBytes: ByteArray,
            entryPoint: String,
            entryMode: PythonEntryMode,
            workspaceParent: File,
            maximumArchiveBytes: Long,
            maximumEntries: Int,
            maximumUncompressedBytes: Long,
            shouldStop: () -> Boolean,
        ): WorkspaceSnapshot {
            require(maximumEntries > 0 && maximumUncompressedBytes > 0L) {
                "Workspace limits are disabled"
            }
            require(sourceBytes.size.toLong() == sourceReference.declaredLengthBytes) {
                "Source snapshot length changed before workspace staging"
            }
            require(MessageDigest.getInstance("SHA-256").digest(sourceBytes)
                .contentEquals(sourceReference.sha256.toByteArray())) {
                "Source snapshot digest changed before workspace staging"
            }

            ensureDirectoryNoSymlink(workspaceParent)
            workspaceParent.listFiles()?.forEach { stale -> runCatching { deleteTreeNoFollow(stale) } }
            val container = createSessionDirectory(workspaceParent)
            val archiveFile = File(container, ARCHIVE_NAME)
            val root = File(container, ROOT_NAME)
            try {
                VerifiedPayloadFile.materialize(
                    reference = reference,
                    descriptor = descriptor,
                    maximumLengthBytes = maximumArchiveBytes,
                    destination = archiveFile,
                    shouldStop = shouldStop,
                ).use { verified ->
                    val centralEntryCount = ZipCentralDirectoryInspector.inspect(
                        verified.requireFile(),
                        maximumEntries,
                    )
                    require(root.mkdir()) { "Workspace root could not be created" }
                    val sourceEntryPoint = workspaceSourceEntryPoint(entryPoint, entryMode)
                    val policy = WorkspaceArchivePathPolicy(sourceEntryPoint)
                    val extractedEntryCount = extractArchive(
                        archive = verified.requireFile(),
                        root = root,
                        policy = policy,
                        maximumEntries = maximumEntries,
                        maximumUncompressedBytes = maximumUncompressedBytes,
                        shouldStop = shouldStop,
                    )
                    require(extractedEntryCount == centralEntryCount) {
                        "Workspace ZIP local and central entry counts differ"
                    }
                    writeSourceEntry(root, sourceEntryPoint, sourceBytes, shouldStop)
                }
                check(!shouldStop()) { "Workspace staging was cancelled" }
                return WorkspaceSnapshot(container, root)
            } catch (error: Throwable) {
                runCatching { deleteTreeNoFollow(container) }
                throw error
            }
        }

        private fun extractArchive(
            archive: File,
            root: File,
            policy: WorkspaceArchivePathPolicy,
            maximumEntries: Int,
            maximumUncompressedBytes: Long,
            shouldStop: () -> Boolean,
        ): Int {
            var entryCount = 0
            var expandedBytes = 0L
            ZipInputStream(BufferedInputStream(FileInputStream(archive))).use { zip ->
                while (true) {
                    check(!shouldStop()) { "Workspace staging was cancelled" }
                    val entry = zip.nextEntry ?: break
                    entryCount++
                    require(entryCount <= maximumEntries) { "Workspace entry count exceeds the provider limit" }
                    require(entry.method == ZipEntry.STORED || entry.method == ZipEntry.DEFLATED) {
                        "Workspace ZIP uses an unsupported compression method"
                    }
                    val path = normalizeArchiveEntry(entry.name, entry.isDirectory)
                    policy.accept(path.logicalPath, path.isDirectory)
                    val destination = resolveWithin(root, path.logicalPath)
                    if (path.isDirectory) {
                        require(zip.read() == -1) { "Workspace ZIP directory entry contains data" }
                        require(!destination.exists() || destination.isDirectory) {
                            "Workspace directory collides with a file"
                        }
                        require(destination.isDirectory || destination.mkdirs()) {
                            "Workspace directory could not be created"
                        }
                    } else {
                        val parent = requireNotNull(destination.parentFile) { "Workspace file has no parent" }
                        require(!parent.exists() || parent.isDirectory) {
                            "Workspace file parent collides with a file"
                        }
                        require(parent.isDirectory || parent.mkdirs()) {
                            "Workspace file parent could not be created"
                        }
                        require(!destination.exists() && destination.createNewFile()) {
                            "Workspace file already exists"
                        }
                        FileOutputStream(destination, false).use { fileOutput ->
                            BufferedOutputStream(fileOutput).use { output ->
                                val buffer = ByteArray(DEFAULT_BUFFER_SIZE)
                                while (true) {
                                    check(!shouldStop()) { "Workspace staging was cancelled" }
                                    val count = zip.read(buffer)
                                    if (count < 0) break
                                    if (count == 0) continue
                                    expandedBytes = Math.addExact(expandedBytes, count.toLong())
                                    require(expandedBytes <= maximumUncompressedBytes) {
                                        "Workspace expanded bytes exceed the provider limit"
                                    }
                                    output.write(buffer, 0, count)
                                }
                            }
                        }
                    }
                    zip.closeEntry()
                }
            }
            return entryCount
        }

        private fun writeSourceEntry(
            root: File,
            entryPoint: String,
            sourceBytes: ByteArray,
            shouldStop: () -> Boolean,
        ) {
            check(!shouldStop()) { "Workspace staging was cancelled" }
            val destination = resolveWithin(root, entryPoint)
            val parent = requireNotNull(destination.parentFile) { "Python entry point has no parent" }
            require(!parent.exists() || parent.isDirectory) { "Python entry point parent collides with a file" }
            require(parent.isDirectory || parent.mkdirs()) { "Python entry point parent could not be created" }
            require(!destination.exists() && destination.createNewFile()) {
                "Workspace archive shadows the Python entry point"
            }
            try {
                FileOutputStream(destination, false).use { output -> output.write(sourceBytes) }
            } catch (error: Throwable) {
                runCatching { destination.delete() }
                throw error
            }
        }

        private fun ensureDirectoryNoSymlink(directory: File) {
            if (!directory.exists()) require(directory.mkdirs()) { "Workspace parent could not be created" }
            val stat = Os.lstat(directory.absolutePath)
            require(OsConstants.S_ISDIR(stat.st_mode)) { "Workspace parent is not a real directory" }
        }

        private fun createSessionDirectory(parent: File): File {
            repeat(8) {
                val candidate = File(parent, "session-${UUID.randomUUID()}")
                if (candidate.mkdir()) return candidate
            }
            error("Workspace session directory could not be created")
        }

        private fun resolveWithin(root: File, logicalPath: String): File {
            val canonicalRoot = root.canonicalFile
            val candidate = File(canonicalRoot, logicalPath).canonicalFile
            val prefix = canonicalRoot.path + File.separator
            require(candidate.path.startsWith(prefix)) { "Workspace path escapes the private root" }
            return candidate
        }

        private const val ARCHIVE_NAME = "workspace.zip"
        private const val ROOT_NAME = "root"
    }
}

internal fun workspaceSourceEntryPoint(entryPoint: String, entryMode: PythonEntryMode): String =
    when (entryMode) {
        PythonEntryMode.FILE -> entryPoint
        PythonEntryMode.MODULE -> PythonRuntimeValidation.fileEntryPointForModuleName(entryPoint)
    }

internal data class WorkspaceArchiveEntryPath(
    val logicalPath: String,
    val isDirectory: Boolean,
)

internal fun normalizeArchiveEntry(name: String, isDirectory: Boolean): WorkspaceArchiveEntryPath {
    require(name.isNotEmpty()) { "Workspace ZIP entry name is empty" }
    require('\\' !in name && name.none(Character::isISOControl)) {
        "Workspace ZIP entry contains a backslash or control character"
    }
    require(Normalizer.normalize(name, Normalizer.Form.NFC) == name) {
        "Workspace ZIP entry is not NFC-normalized"
    }
    require(!name.startsWith('/') && !WINDOWS_DRIVE_PREFIX.matches(name)) {
        "Workspace ZIP entry is absolute"
    }
    require(isDirectory == name.endsWith('/')) { "Workspace ZIP directory marker is inconsistent" }
    val logical = if (isDirectory) name.dropLast(1) else name
    require(logical.isNotEmpty() && !logical.endsWith('/')) { "Workspace ZIP entry has an empty segment" }
    require(logical.toByteArray(StandardCharsets.UTF_8).size <= MAX_LOGICAL_PATH_BYTES) {
        "Workspace ZIP entry path is too long"
    }
    val segments = logical.split('/')
    require(segments.none { segment ->
        segment.isEmpty() || segment == "." || segment == ".." ||
            segment.toByteArray(StandardCharsets.UTF_8).size > MAX_PATH_SEGMENT_BYTES
    }) { "Workspace ZIP entry contains an unsafe path segment" }
    return WorkspaceArchiveEntryPath(logical, isDirectory)
}

/** Rejects case aliases, file/directory prefix conflicts, and any SOURCE entry-point shadow. */
internal class WorkspaceArchivePathPolicy(entryPoint: String) {
    private enum class Kind { FILE, DIRECTORY }

    private val entryPointKey = caseKey(entryPoint)
    private val seen = HashMap<String, Kind>()
    private val requiredDirectories = HashSet<String>()
    private val directorySpellings = HashMap<String, String>()

    init {
        recordAncestors(entryPoint)
    }

    fun accept(logicalPath: String, isDirectory: Boolean) {
        val key = caseKey(logicalPath)
        val kind = if (isDirectory) Kind.DIRECTORY else Kind.FILE
        require(key != entryPointKey && !key.startsWith("$entryPointKey/")) {
            "Workspace archive shadows the Python entry point"
        }
        require(!(entryPointKey.startsWith("$key/") && kind == Kind.FILE)) {
            "Workspace archive file shadows an entry-point directory"
        }
        require(seen.putIfAbsent(key, kind) == null) {
            "Workspace archive contains a duplicate or case-fold collision"
        }
        if (kind == Kind.FILE) {
            require(key !in requiredDirectories) { "Workspace archive contains a file/directory prefix conflict" }
        }
        recordAncestors(logicalPath)
        if (kind == Kind.DIRECTORY) {
            val existing = directorySpellings.putIfAbsent(key, logicalPath)
            require(existing == null || existing == logicalPath) {
                "Workspace archive contains a case-fold directory collision"
            }
            requiredDirectories += key
        }
    }

    private fun recordAncestors(path: String) {
        val segments = path.split('/')
        var prefix = ""
        for (index in 0 until segments.lastIndex) {
            prefix = if (prefix.isEmpty()) segments[index] else "$prefix/${segments[index]}"
            val prefixKey = caseKey(prefix)
            require(seen[prefixKey] != Kind.FILE) { "Workspace archive contains a file/directory prefix conflict" }
            val existing = directorySpellings.putIfAbsent(prefixKey, prefix)
            require(existing == null || existing == prefix) {
                "Workspace archive contains a case-fold directory collision"
            }
            requiredDirectories += prefixKey
        }
    }

    private fun caseKey(path: String): String = path
        .uppercase(Locale.ROOT)
        .lowercase(Locale.ROOT)
}

/** Minimal central-directory audit used only to reject unsupported/symlink-like ZIPs. */
private object ZipCentralDirectoryInspector {
    fun inspect(file: File, maximumEntries: Int): Int = RandomAccessFile(file, "r").use { input ->
        val fileLength = input.length()
        require(fileLength >= EOCD_MIN_BYTES) { "Workspace payload is not a ZIP archive" }
        val tailLength = minOf(fileLength, EOCD_MAX_SEARCH_BYTES).toInt()
        val tail = ByteArray(tailLength)
        input.seek(fileLength - tailLength)
        input.readFully(tail)
        val eocdIndex = findEocd(tail)
        require(eocdIndex >= 0) { "Workspace ZIP end record is missing or malformed" }
        val eocdOffset = fileLength - tailLength + eocdIndex
        val diskNumber = u16(tail, eocdIndex + 4)
        val centralDisk = u16(tail, eocdIndex + 6)
        val entriesOnDisk = u16(tail, eocdIndex + 8)
        val totalEntries = u16(tail, eocdIndex + 10)
        val centralSize = u32(tail, eocdIndex + 12)
        val centralOffset = u32(tail, eocdIndex + 16)
        require(diskNumber == 0 && centralDisk == 0 && entriesOnDisk == totalEntries) {
            "Multi-disk workspace ZIPs are unsupported"
        }
        require(totalEntries != ZIP64_U16 && centralSize != ZIP64_U32 && centralOffset != ZIP64_U32) {
            "ZIP64 workspace archives are unsupported"
        }
        require(totalEntries <= maximumEntries) { "Workspace entry count exceeds the provider limit" }
        require(centralOffset + centralSize == eocdOffset) { "Workspace ZIP central directory is inconsistent" }
        if (totalEntries > 0) {
            input.seek(0L)
            require(readU32(input) == LOCAL_FILE_HEADER_SIGNATURE) {
                "Self-extracting workspace ZIPs are unsupported"
            }
        }

        input.seek(centralOffset)
        val fixed = ByteArray(CENTRAL_HEADER_BYTES)
        repeat(totalEntries) {
            input.readFully(fixed)
            require(u32(fixed, 0) == CENTRAL_FILE_HEADER_SIGNATURE) {
                "Workspace ZIP central directory entry is malformed"
            }
            val versionMadeBy = u16(fixed, 4)
            val flags = u16(fixed, 8)
            val method = u16(fixed, 10)
            val compressedSize = u32(fixed, 20)
            val uncompressedSize = u32(fixed, 24)
            val nameLength = u16(fixed, 28)
            val extraLength = u16(fixed, 30)
            val commentLength = u16(fixed, 32)
            val startingDisk = u16(fixed, 34)
            val externalAttributes = u32(fixed, 38)
            val localHeaderOffset = u32(fixed, 42)
            require(flags and ENCRYPTION_FLAGS == 0) { "Encrypted workspace ZIP entries are unsupported" }
            require(method == ZipEntry.STORED || method == ZipEntry.DEFLATED) {
                "Workspace ZIP uses an unsupported compression method"
            }
            require(
                compressedSize != ZIP64_U32 && uncompressedSize != ZIP64_U32 &&
                    localHeaderOffset != ZIP64_U32 && startingDisk != ZIP64_U16,
            ) { "ZIP64 workspace entries are unsupported" }
            rejectSpecialUnixEntry(versionMadeBy, externalAttributes)
            val variableLength = nameLength.toLong() + extraLength.toLong() + commentLength.toLong()
            require(input.filePointer + variableLength <= centralOffset + centralSize) {
                "Workspace ZIP central directory entry exceeds its boundary"
            }
            input.seek(input.filePointer + variableLength)
        }
        require(input.filePointer == centralOffset + centralSize) {
            "Workspace ZIP central directory has trailing records"
        }
        totalEntries
    }

    private fun findEocd(tail: ByteArray): Int {
        for (index in tail.size - EOCD_MIN_BYTES downTo 0) {
            if (u32(tail, index) != EOCD_SIGNATURE) continue
            val commentLength = u16(tail, index + 20)
            if (index + EOCD_MIN_BYTES + commentLength == tail.size) return index
        }
        return -1
    }

    private fun rejectSpecialUnixEntry(versionMadeBy: Int, externalAttributes: Long) {
        val creatorSystem = versionMadeBy ushr 8
        if (creatorSystem != UNIX_CREATOR_SYSTEM) return
        val mode = ((externalAttributes ushr 16) and 0xffffL).toInt()
        val type = mode and UNIX_FILE_TYPE_MASK
        require(type == 0 || type == UNIX_REGULAR_FILE || type == UNIX_DIRECTORY) {
            "Workspace ZIP contains a symlink or special Unix entry"
        }
    }

    private fun readU32(input: RandomAccessFile): Long {
        val bytes = ByteArray(4)
        input.readFully(bytes)
        return u32(bytes, 0)
    }

    private const val EOCD_MIN_BYTES = 22
    private const val EOCD_MAX_SEARCH_BYTES = EOCD_MIN_BYTES + 65_535L
    private const val CENTRAL_HEADER_BYTES = 46
    private const val EOCD_SIGNATURE = 0x06054b50L
    private const val CENTRAL_FILE_HEADER_SIGNATURE = 0x02014b50L
    private const val LOCAL_FILE_HEADER_SIGNATURE = 0x04034b50L
    private const val ZIP64_U16 = 0xffff
    private const val ZIP64_U32 = 0xffff_ffffL
    private const val ENCRYPTION_FLAGS = 0x0041
    private const val UNIX_CREATOR_SYSTEM = 3
    private const val UNIX_FILE_TYPE_MASK = 0xf000
    private const val UNIX_REGULAR_FILE = 0x8000
    private const val UNIX_DIRECTORY = 0x4000
}

private fun u16(bytes: ByteArray, offset: Int): Int =
    (bytes[offset].toInt() and 0xff) or ((bytes[offset + 1].toInt() and 0xff) shl 8)

private fun u32(bytes: ByteArray, offset: Int): Long =
    u16(bytes, offset).toLong() or (u16(bytes, offset + 2).toLong() shl 16)

private fun deleteTreeNoFollow(file: File) {
    val stat = try {
        Os.lstat(file.absolutePath)
    } catch (error: ErrnoException) {
        if (error.errno == OsConstants.ENOENT) return
        throw error
    }
    if (OsConstants.S_ISDIR(stat.st_mode)) {
        file.listFiles()?.forEach(::deleteTreeNoFollow)
        runCatching { Os.remove(file.absolutePath) }
    } else {
        runCatching { Os.remove(file.absolutePath) }
    }
}

private val WINDOWS_DRIVE_PREFIX = Regex("^[A-Za-z]:.*")
private const val MAX_LOGICAL_PATH_BYTES = 4096
private const val MAX_PATH_SEGMENT_BYTES = 255
