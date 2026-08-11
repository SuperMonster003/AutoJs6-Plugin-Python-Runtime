package io.github.supermonster003.autojs6.plugin.python.runtime.transport

import android.os.ParcelFileDescriptor
import org.autojs.plugin.python.runtime.api.PythonPayloadReference
import java.io.Closeable
import java.security.MessageDigest

internal class SourceSnapshot private constructor(
    private var source: ByteArray?,
) : Closeable {
    @Synchronized
    fun copyBytes(): ByteArray = checkNotNull(source) { "Source snapshot is closed" }.copyOf()

    @Synchronized
    override fun close() {
        source?.fill(0)
        source = null
    }

    companion object {
        fun materialize(
            reference: PythonPayloadReference,
            descriptor: ParcelFileDescriptor,
            maximumLengthBytes: Long,
            shouldStop: () -> Boolean,
        ): SourceSnapshot {
            require(reference.declaredLengthBytes in 0L..maximumLengthBytes) {
                "Source exceeds the provider limit"
            }
            require(reference.declaredLengthBytes <= Int.MAX_VALUE.toLong()) {
                "Source cannot be materialized in memory"
            }
            val digest = MessageDigest.getInstance("SHA-256")
            val output = ByteArray(reference.declaredLengthBytes.toInt())
            try {
                ParcelFileDescriptor.AutoCloseInputStream(descriptor).use { input ->
                    var offset = 0
                    while (offset < output.size) {
                        check(!shouldStop()) { "Source staging was cancelled" }
                        val count = input.read(output, offset, output.size - offset)
                        require(count >= 0) { "Source ended before its declared length" }
                        if (count == 0) continue
                        digest.update(output, offset, count)
                        offset += count
                    }
                    check(!shouldStop()) { "Source staging was cancelled" }
                    require(input.read() == -1) { "Source exceeds its declared length" }
                    if (descriptor.canDetectErrors()) descriptor.checkError()
                }
                require(digest.digest().contentEquals(reference.sha256.toByteArray())) {
                    "Source digest does not match"
                }
                return SourceSnapshot(output)
            } catch (error: Throwable) {
                output.fill(0)
                throw error
            }
        }
    }
}
