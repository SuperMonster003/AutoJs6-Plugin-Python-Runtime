package io.github.supermonster003.autojs6.plugin.python.runtime.transport

import android.os.ParcelFileDescriptor
import android.system.Os
import android.system.OsConstants
import org.autojs.plugin.python.runtime.api.PythonOutputArtifact
import org.autojs.plugin.python.runtime.api.PythonRequestId
import org.autojs.plugin.python.runtime.api.PythonResultPolicy
import org.autojs.plugin.python.runtime.api.PythonRuntimeValidation
import org.autojs.plugin.python.runtime.api.PythonSha256
import java.io.Closeable
import java.io.File
import java.io.FileInputStream
import java.io.FileOutputStream
import java.security.MessageDigest
import java.util.UUID
import java.util.concurrent.atomic.AtomicBoolean

/**
 * One Plugin-private writable result root. User files are copied into immutable private snapshots
 * only after Python returns; no writable script file is ever sent across Binder.
 */
internal class OutputArtifactWorkspace private constructor(
    val root: File,
    private val parent: File,
) : Closeable {
    private val claimed = AtomicBoolean(false)
    private val closed = AtomicBoolean(false)

    fun prepare(
        paths: Collection<String>,
        policy: PythonResultPolicy,
        shouldStop: () -> Boolean,
    ): PreparedOutputArtifacts {
        check(!closed.get() && claimed.compareAndSet(false, true)) {
            "Python output artifact workspace was already consumed"
        }
        PythonRuntimeValidation.validateResultPolicy(policy)
        require(paths.size <= policy.maxArtifacts) {
            "Python output artifact count exceeds the negotiated limit"
        }
        require(paths.size == paths.toSet().size) {
            "Python output artifact paths contain duplicates"
        }
        if (paths.isEmpty()) {
            closed.set(true)
            return PreparedOutputArtifacts(emptyList(), emptyArray(), listOf(root), parent)
        }

        val snapshotRoot = privateDirectory(parent, "snapshot-")
        val artifacts = ArrayList<PythonOutputArtifact>(paths.size)
        val snapshotFiles = ArrayList<File>(paths.size)
        var aggregateBytes = 0L
        try {
            paths.forEachIndexed { index, path ->
                if (shouldStop()) throw InterruptedException("Python output artifact capture was cancelled")
                PythonRuntimeValidation.validateOutputArtifactPath(path, policy.maxArtifactPathBytes)
                val source = resolveRegularArtifact(path)
                val snapshot = File(snapshotRoot, "artifact-$index.bin")
                val captured = captureRegularFile(
                    source = source,
                    destination = snapshot,
                    maximumBytes = policy.maxArtifactBytes,
                    shouldStop = shouldStop,
                )
                aggregateBytes = Math.addExact(aggregateBytes, captured.lengthBytes)
                require(aggregateBytes <= policy.maxTotalArtifactBytes) {
                    "Python output artifacts exceed the negotiated aggregate limit"
                }
                artifacts += PythonOutputArtifact(
                    path = path,
                    descriptorIndex = index,
                    declaredLengthBytes = captured.lengthBytes,
                    sha256 = captured.sha256,
                ).also(PythonRuntimeValidation::validateOutputArtifact)
                snapshotFiles += snapshot
            }

            val descriptors = ArrayList<ParcelFileDescriptor>(snapshotFiles.size)
            try {
                snapshotFiles.forEachIndexed { index, file ->
                    val descriptor = ParcelFileDescriptor.open(file, ParcelFileDescriptor.MODE_READ_ONLY)
                    check(descriptor.statSize == artifacts[index].declaredLengthBytes) {
                        "Python output artifact snapshot changed while opening its descriptor"
                    }
                    descriptors += descriptor
                }
                closed.set(true)
                return PreparedOutputArtifacts(
                    artifacts = artifacts,
                    descriptors = descriptors.toTypedArray(),
                    cleanupRoots = listOf(snapshotRoot, root),
                    parent = parent,
                )
            } catch (error: Throwable) {
                descriptors.forEach { runCatching { it.close() } }
                throw error
            }
        } catch (error: Throwable) {
            closed.set(true)
            deleteTree(snapshotRoot, parent)
            deleteTree(root, parent)
            throw error
        }
    }

    private fun resolveRegularArtifact(path: String): File {
        var current = root
        val segments = path.split('/')
        segments.forEachIndexed { index, segment ->
            current = File(current, segment)
            val stat = Os.lstat(current.path)
            val final = index == segments.lastIndex
            if (final) {
                require(OsConstants.S_ISREG(stat.st_mode) && !OsConstants.S_ISLNK(stat.st_mode)) {
                    "Python output artifact is not a regular file"
                }
            } else {
                require(OsConstants.S_ISDIR(stat.st_mode) && !OsConstants.S_ISLNK(stat.st_mode)) {
                    "Python output artifact parent is not a regular directory"
                }
            }
        }
        val canonical = current.canonicalFile
        require(canonical.path.startsWith(root.path + File.separator)) {
            "Python output artifact escaped its private root"
        }
        return canonical
    }

    override fun close() {
        if (!closed.compareAndSet(false, true)) return
        deleteTree(root, parent)
    }

    companion object {
        // Linux O_CLOEXEC is stable across Android ABIs (bionic asm-generic/fcntl.h).
        // Its android.system.OsConstants field was only exposed in API 27; the
        // inline value keeps atomic close-on-exec protection on our API 24 floor.
        private const val OPEN_CLOSE_ON_EXEC = 0x80000

        fun create(parentDirectory: File, requestId: PythonRequestId): OutputArtifactWorkspace {
            val parent = parentDirectory.canonicalFile
            check((parent.isDirectory || parent.mkdirs()) && parent.isDirectory) {
                "Python output artifact parent is unavailable"
            }
            val root = privateDirectory(parent, "result-${requestId}-")
            return OutputArtifactWorkspace(root, parent)
        }

        private fun privateDirectory(parent: File, prefix: String): File {
            val directory = File(parent, prefix + UUID.randomUUID()).canonicalFile
            require(directory.parentFile == parent && directory.mkdir()) {
                "Python output artifact private directory is unavailable"
            }
            directory.setReadable(false, false)
            directory.setWritable(false, false)
            directory.setExecutable(false, false)
            check(
                directory.setReadable(true, true) &&
                    directory.setWritable(true, true) &&
                    directory.setExecutable(true, true),
            ) { "Python output artifact private directory permissions could not be restricted" }
            return directory
        }

        private fun captureRegularFile(
            source: File,
            destination: File,
            maximumBytes: Long,
            shouldStop: () -> Boolean,
        ): CapturedArtifact {
            val before = Os.lstat(source.path)
            require(OsConstants.S_ISREG(before.st_mode) && !OsConstants.S_ISLNK(before.st_mode)) {
                "Python output artifact is not a regular file"
            }
            val descriptor = Os.open(
                source.path,
                OsConstants.O_RDONLY or OPEN_CLOSE_ON_EXEC or OsConstants.O_NOFOLLOW,
                0,
            )
            val digest = MessageDigest.getInstance("SHA-256")
            var total = 0L
            try {
                FileInputStream(descriptor).use { input ->
                    val opened = Os.fstat(input.fd)
                    require(
                        OsConstants.S_ISREG(opened.st_mode) &&
                            opened.st_dev == before.st_dev &&
                            opened.st_ino == before.st_ino,
                    ) { "Python output artifact changed while it was opened" }
                    FileOutputStream(destination, false).use { output ->
                        val buffer = ByteArray(COPY_BUFFER_BYTES)
                        while (true) {
                            if (shouldStop()) {
                                throw InterruptedException("Python output artifact capture was cancelled")
                            }
                            val count = input.read(buffer)
                            if (count < 0) break
                            if (count == 0) continue
                            total = Math.addExact(total, count.toLong())
                            require(total <= maximumBytes) {
                                "Python output artifact exceeds the negotiated byte limit"
                            }
                            output.write(buffer, 0, count)
                            digest.update(buffer, 0, count)
                        }
                        output.flush()
                        output.fd.sync()
                    }
                }
            } catch (error: Throwable) {
                runCatching { Os.close(descriptor) }
                destination.delete()
                throw error
            }
            val after = Os.lstat(source.path)
            require(
                OsConstants.S_ISREG(after.st_mode) &&
                    after.st_dev == before.st_dev &&
                    after.st_ino == before.st_ino &&
                    after.st_size == total,
            ) { "Python output artifact changed during capture" }
            destination.setWritable(false, false)
            destination.setReadable(true, true)
            return CapturedArtifact(total, PythonSha256.fromBytes(digest.digest()))
        }

        internal fun deleteTree(target: File, expectedParent: File) {
            val canonicalParent = expectedParent.canonicalFile
            val absolute = target.absoluteFile
            if (absolute.parentFile?.canonicalFile != canonicalParent &&
                !absolute.path.startsWith(canonicalParent.path + File.separator)
            ) {
                return
            }
            deleteNode(absolute)
        }

        private fun deleteNode(node: File) {
            val stat = runCatching { Os.lstat(node.path) }.getOrNull() ?: return
            if (OsConstants.S_ISDIR(stat.st_mode) && !OsConstants.S_ISLNK(stat.st_mode)) {
                node.listFiles()?.forEach(::deleteNode)
            }
            node.delete()
        }

        private const val COPY_BUFFER_BYTES = 64 * 1024
    }

    private data class CapturedArtifact(
        val lengthBytes: Long,
        val sha256: PythonSha256,
    )
}

internal class PreparedOutputArtifacts(
    val artifacts: List<PythonOutputArtifact>,
    val descriptors: Array<ParcelFileDescriptor>,
    private val cleanupRoots: List<File>,
    private val parent: File,
) : Closeable {
    private val closed = AtomicBoolean(false)

    override fun close() {
        if (!closed.compareAndSet(false, true)) return
        descriptors.forEach { runCatching { it.close() } }
        cleanupRoots.forEach { OutputArtifactWorkspace.deleteTree(it, parent) }
    }
}
