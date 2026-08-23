package io.github.supermonster003.autojs6.plugin.python.runtime.execution

import org.autojs.plugin.python.runtime.api.IPythonHostCapabilityBroker
import org.autojs.plugin.python.runtime.api.PythonRuntimeContract
import java.nio.ByteBuffer
import java.nio.CharBuffer
import java.nio.charset.CodingErrorAction
import java.nio.charset.StandardCharsets
import java.util.concurrent.atomic.AtomicBoolean

/**
 * The only live Host object exposed to the private bootstrap. User globals receive Python
 * functions backed by strict JSON, never this Binder interface or another Java capability.
 */
internal class ChaquopyHostCapabilityBridge(
    private val remoteDispatch: (ByteArray) -> ByteArray?,
) : AutoCloseable {
    constructor(remote: IPythonHostCapabilityBroker) : this(remote::dispatch)

    private val closed = AtomicBoolean(false)

    fun dispatch(requestJson: String?): String {
        check(!closed.get()) { "AutoJs6 host capability broker is closed" }
        val request = requireNotNull(requestJson) { "AutoJs6 host capability request is null" }
        val encodedRequest = strictUtf8(request)
        require(encodedRequest.size in 1..PythonRuntimeContract.MAX_HOST_CAPABILITY_REQUEST_BYTES) {
            "AutoJs6 host capability request exceeds the byte limit"
        }
        val encodedResponse = try {
            requireNotNull(remoteDispatch(encodedRequest)) {
                "AutoJs6 host capability response is null"
            }
        } catch (error: Exception) {
            close()
            throw IllegalStateException("AutoJs6 host capability broker is unavailable", error)
        }
        check(!closed.get()) { "AutoJs6 host capability broker closed during dispatch" }
        require(encodedResponse.size in 1..PythonRuntimeContract.MAX_HOST_CAPABILITY_RESPONSE_BYTES) {
            "AutoJs6 host capability response exceeds the byte limit"
        }
        return strictUtf8(encodedResponse)
    }

    override fun close() {
        closed.set(true)
    }

    private fun strictUtf8(value: String): ByteArray = runCatching {
        val buffer = StandardCharsets.UTF_8
            .newEncoder()
            .onMalformedInput(CodingErrorAction.REPORT)
            .onUnmappableCharacter(CodingErrorAction.REPORT)
            .encode(CharBuffer.wrap(value))
        ByteArray(buffer.remaining()).also(buffer::get)
    }.getOrElse { throw IllegalArgumentException("AutoJs6 host capability request is not UTF-8", it) }

    private fun strictUtf8(value: ByteArray): String = runCatching {
        StandardCharsets.UTF_8
            .newDecoder()
            .onMalformedInput(CodingErrorAction.REPORT)
            .onUnmappableCharacter(CodingErrorAction.REPORT)
            .decode(ByteBuffer.wrap(value))
            .toString()
    }.getOrElse { throw IllegalArgumentException("AutoJs6 host capability response is not UTF-8", it) }
}
