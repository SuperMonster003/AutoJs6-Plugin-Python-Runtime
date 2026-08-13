package io.github.supermonster003.autojs6.plugin.python.runtime.transport

import android.os.ParcelFileDescriptor
import org.autojs.plugin.python.runtime.api.PythonPayloadKind
import org.autojs.plugin.python.runtime.api.PythonPayloadReference
import java.io.Closeable

/** Complete, digest-checked stdin bytes owned by one execution. */
internal class StdinSnapshot private constructor(
    private val payload: SourceSnapshot,
) : Closeable {
    fun copyBytes(): ByteArray = payload.copyBytes()

    override fun close() = payload.close()

    companion object {
        fun materialize(
            reference: PythonPayloadReference,
            descriptor: ParcelFileDescriptor,
            maximumLengthBytes: Long,
            shouldStop: () -> Boolean,
        ): StdinSnapshot {
            require(reference.kind == PythonPayloadKind.STDIN) {
                "Stdin descriptor has the wrong payload kind"
            }
            return StdinSnapshot(
                SourceSnapshot.materialize(
                    reference = reference,
                    descriptor = descriptor,
                    maximumLengthBytes = maximumLengthBytes,
                    shouldStop = shouldStop,
                ),
            )
        }
    }
}
