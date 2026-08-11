package io.github.supermonster003.autojs6.plugin.python.runtime.transport

import android.os.ParcelFileDescriptor
import org.autojs.plugin.python.runtime.api.PythonPayloadReference
import java.io.BufferedOutputStream
import java.io.Closeable
import java.io.File
import java.io.FileOutputStream
import java.security.MessageDigest
import java.util.concurrent.atomic.AtomicReference

/** A provider-private, exact-length and digest-verified payload snapshot. */
internal class VerifiedPayloadFile private constructor(file: File) : Closeable {
    private val ownedFile = AtomicReference(file)

    fun requireFile(): File = checkNotNull(ownedFile.get()) { "Payload snapshot is closed" }

    override fun close() {
        ownedFile.getAndSet(null)?.let { file -> runCatching { file.delete() } }
    }

    companion object {
        fun materialize(
            reference: PythonPayloadReference,
            descriptor: ParcelFileDescriptor,
            maximumLengthBytes: Long,
            destination: File,
            shouldStop: () -> Boolean,
        ): VerifiedPayloadFile {
            require(reference.declaredLengthBytes in 1L..maximumLengthBytes) {
                "Payload exceeds the provider limit"
            }
            require(!destination.exists()) { "Payload snapshot destination already exists" }
            require(destination.parentFile?.isDirectory == true) { "Payload snapshot parent is unavailable" }

            val digest = MessageDigest.getInstance("SHA-256")
            try {
                ParcelFileDescriptor.AutoCloseInputStream(descriptor).use { input ->
                    FileOutputStream(destination, false).use { fileOutput ->
                        BufferedOutputStream(fileOutput).use { output ->
                            val buffer = ByteArray(DEFAULT_BUFFER_SIZE)
                            var remaining = reference.declaredLengthBytes
                            while (remaining > 0L) {
                                check(!shouldStop()) { "Payload staging was cancelled" }
                                val requested = minOf(buffer.size.toLong(), remaining).toInt()
                                val count = input.read(buffer, 0, requested)
                                require(count >= 0) { "Payload ended before its declared length" }
                                if (count == 0) continue
                                output.write(buffer, 0, count)
                                digest.update(buffer, 0, count)
                                remaining -= count.toLong()
                            }
                            output.flush()
                            check(!shouldStop()) { "Payload staging was cancelled" }
                            require(input.read() == -1) { "Payload exceeds its declared length" }
                            if (descriptor.canDetectErrors()) descriptor.checkError()
                        }
                    }
                }
                require(digest.digest().contentEquals(reference.sha256.toByteArray())) {
                    "Payload digest does not match"
                }
                return VerifiedPayloadFile(destination)
            } catch (error: Throwable) {
                runCatching { destination.delete() }
                throw error
            }
        }
    }
}
