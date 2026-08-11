package io.github.supermonster003.autojs6.plugin.python.runtime.transport

import org.autojs.plugin.protocol.wire.TaggedWireDocument
import org.autojs.plugin.protocol.wire.TaggedWireLimits
import org.autojs.plugin.python.runtime.api.PythonRequestId
import org.autojs.plugin.python.runtime.api.PythonRuntimeContract

/** Recovers only the unique request ID before the remainder of an envelope is trusted. */
internal object PythonRequestEnvelope {
    private const val REQUEST_ID_TAG = 1
    private val limits = TaggedWireLimits(
        maxDocumentBytes = PythonRuntimeContract.MAX_METADATA_BYTES,
        maxFieldBytes = 64 * 1024,
        maxFields = 1024,
    )

    fun requireUniqueRequestId(bytes: ByteArray): PythonRequestId = TaggedWireDocument
        .decode(bytes, limits)
        .requireSchema(PythonRuntimeContract.SCHEMA_EXECUTION_REQUEST, PythonRuntimeContract.SCHEMA_MAJOR)
        .validateKnownCardinality(setOf(REQUEST_ID_TAG))
        .requireBytes(REQUEST_ID_TAG)
        .let(PythonRequestId::fromBytes)
}
