package io.github.supermonster003.autojs6.plugin.python.runtime.transport

import java.nio.ByteBuffer
import java.nio.charset.CodingErrorAction
import java.nio.charset.StandardCharsets

/** Admission policy for the documented UTF-8-only Python source contract. */
internal object Utf8SourcePolicy {
    private val codingCookie = Regex(
        pattern = "^[\\t\\f ]*#.*?coding[:=][\\t ]*([-_.a-zA-Z0-9]+)",
        option = RegexOption.IGNORE_CASE,
    )
    private val allowedCodingCookies = setOf("utf8", "utf-8", "utf-8-sig")

    fun requireValid(source: ByteArray) {
        require(source.none { it == 0.toByte() }) { "Python source contains a NUL byte" }
        val decoded = StandardCharsets.UTF_8.newDecoder()
            .onMalformedInput(CodingErrorAction.REPORT)
            .onUnmappableCharacter(CodingErrorAction.REPORT)
            .decode(ByteBuffer.wrap(source))
            .toString()
            .removePrefix("\uFEFF")
        decoded.lineSequence().take(2).forEach { line ->
            val encoding = codingCookie.find(line)?.groupValues?.get(1) ?: return@forEach
            val normalized = encoding.lowercase().replace('_', '-')
            require(normalized in allowedCodingCookies) {
                "Python source declares a non-UTF-8 encoding"
            }
        }
    }
}
