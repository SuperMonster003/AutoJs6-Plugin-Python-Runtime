package io.github.supermonster003.autojs6.plugin.python.runtime.transport

import android.os.ParcelFileDescriptor
import org.autojs.plugin.python.runtime.api.PythonPayloadReference
import java.io.Closeable

internal class OwnedParcelFileDescriptors private constructor(
    descriptors: List<ParcelFileDescriptor>,
) : Closeable {
    private val descriptors = descriptors.map<ParcelFileDescriptor, ParcelFileDescriptor?> { it }.toTypedArray()

    fun consume(reference: PythonPayloadReference, block: (ParcelFileDescriptor) -> Unit) {
        val descriptor = synchronized(descriptors) {
            require(reference.descriptorIndex in descriptors.indices) { "Descriptor index is out of range" }
            checkNotNull(descriptors[reference.descriptorIndex]) { "Descriptor was already consumed or closed" }
        }
        try {
            block(descriptor)
        } finally {
            synchronized(descriptors) {
                if (descriptors[reference.descriptorIndex] === descriptor) {
                    descriptors[reference.descriptorIndex] = null
                }
            }
            closeQuietly(descriptor)
        }
    }

    override fun close() {
        val pending = synchronized(descriptors) {
            descriptors.mapIndexedNotNull { index, descriptor ->
                descriptor?.also { descriptors[index] = null }
            }
        }
        pending.forEach(::closeQuietly)
    }

    companion object {
        /**
         * Atomically adopts Binder-unmarshalled receiver copies. Retaining these complete PFD
         * objects preserves a reliable pipe's data and error-channel descriptors; raw-fd dup
         * would copy only the data descriptor and silently discard closeWithError evidence.
         */
        fun takeReceiverCopies(incoming: Array<out ParcelFileDescriptor?>): OwnedParcelFileDescriptors =
            OwnedParcelFileDescriptors(
                incoming.mapIndexed { index, descriptor ->
                    requireNotNull(descriptor) { "Descriptor $index is null" }
                },
            )

        fun closeIncoming(incoming: Array<out ParcelFileDescriptor?>?) {
            incoming?.forEach(::closeQuietly)
        }

        private fun closeQuietly(descriptor: ParcelFileDescriptor?) {
            runCatching { descriptor?.close() }
        }
    }
}
