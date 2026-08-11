package io.github.supermonster003.autojs6.plugin.python.runtime.transport

import android.os.ParcelFileDescriptor
import org.autojs.plugin.python.runtime.api.PythonPayloadKind
import org.autojs.plugin.python.runtime.api.PythonPayloadReference
import org.autojs.plugin.python.runtime.api.PythonRuntimeContract
import java.io.Closeable
import java.nio.ByteBuffer
import java.nio.charset.CodingErrorAction
import java.nio.charset.StandardCharsets

/** A validated, execution-bound copy of the host's frozen read-only capability document. */
internal class HostCapabilitySnapshot private constructor(
    private var encoded: ByteArray?,
) : Closeable {

    @Synchronized
    fun copyBytes(): ByteArray = checkNotNull(encoded) {
        "Host capability snapshot is closed"
    }.copyOf()

    @Synchronized
    override fun close() {
        encoded?.fill(0)
        encoded = null
    }

    companion object {
        fun materialize(
            reference: PythonPayloadReference,
            descriptor: ParcelFileDescriptor,
            maximumLengthBytes: Long,
            expectedExecutionId: String,
            expectedEntryPoint: String,
            expectedProjectFilesAvailable: Boolean,
            shouldStop: () -> Boolean,
        ): HostCapabilitySnapshot {
            require(reference.kind == PythonPayloadKind.HOST_CAPABILITY_SNAPSHOT) {
                "Host capability descriptor has the wrong payload kind"
            }
            val bytes = SourceSnapshot.materialize(
                reference = reference,
                descriptor = descriptor,
                maximumLengthBytes = maximumLengthBytes,
                shouldStop = shouldStop,
            ).use { snapshot -> snapshot.copyBytes() }
            return try {
                HostCapabilitySnapshotPolicy.validate(
                    encoded = bytes,
                    expectedExecutionId = expectedExecutionId,
                    expectedEntryPoint = expectedEntryPoint,
                    expectedProjectFilesAvailable = expectedProjectFilesAvailable,
                )
                HostCapabilitySnapshot(bytes)
            } catch (error: Throwable) {
                bytes.fill(0)
                throw error
            }
        }
    }
}

internal data class ValidatedHostCapabilitySnapshot(
    val executionId: String,
    val entryPoint: String,
    val projectFilesAvailable: Boolean,
    val grants: Set<String>,
    val packageName: String,
    val versionName: String,
    val versionCode: Long,
    val debuggable: Boolean,
    val sdkInt: Int,
    val release: String,
    val manufacturer: String,
    val brand: String,
    val model: String,
    val supportedAbis: List<String>,
)

/** Strict schema validation before any snapshot byte reaches CPython. */
internal object HostCapabilitySnapshotPolicy {
    private val MAX_DOCUMENT_BYTES = PythonRuntimeContract.MAX_HOST_CAPABILITY_SNAPSHOT_BYTES.toInt()
    private const val MAX_TEXT_BYTES = 4 * 1024
    private const val MAX_ABIS = 8
    private const val GRANT_APP = "app.snapshot.read"
    private const val GRANT_DEVICE = "device.snapshot.read"
    private const val GRANT_PROJECT = "project.files.read"

    fun validate(
        encoded: ByteArray,
        expectedExecutionId: String,
        expectedEntryPoint: String,
        expectedProjectFilesAvailable: Boolean,
    ): ValidatedHostCapabilitySnapshot {
        require(encoded.isNotEmpty() && encoded.size <= MAX_DOCUMENT_BYTES) {
            "Host capability snapshot size is invalid"
        }
        val root = StrictJsonParser(decodeUtf8(encoded)).parse().asObject("snapshot")
        root.requireExactKeys("schemaVersion", "execution", "grants", "app", "device")
        require(root.long("schemaVersion") == 1L) { "Host capability snapshot schema is unsupported" }

        val execution = root.objectValue("execution")
        execution.requireExactKeys("id", "entryPoint", "project")
        val executionId = execution.string("id")
        val entryPoint = execution.string("entryPoint")
        val project = execution.boolean("project")
        require(executionId == expectedExecutionId) { "Host capability execution ID does not match" }
        require(entryPoint == expectedEntryPoint) { "Host capability entry point does not match" }
        require(project == expectedProjectFilesAvailable) {
            "Host capability project availability does not match the staged workspace"
        }
        requireSafeText(entryPoint, "Host capability entry point")

        val grants = root.array("grants").values.mapIndexed { index, value ->
            value.asString("grant $index").also { requireSafeText(it, "Host capability grant") }
        }
        require(grants.distinct().size == grants.size) { "Host capability grants contain duplicates" }
        val expectedGrants = buildSet {
            add(GRANT_APP)
            add(GRANT_DEVICE)
            if (project) add(GRANT_PROJECT)
        }
        require(grants.toSet() == expectedGrants) { "Host capability grants are missing or unsupported" }

        val app = root.objectValue("app")
        app.requireExactKeys("packageName", "versionName", "versionCode", "debuggable")
        val packageName = app.string("packageName")
        val versionName = app.string("versionName")
        val versionCode = app.long("versionCode")
        requireSafeText(packageName, "Host package name", allowEmpty = false)
        requireSafeText(versionName, "Host version name")
        require(versionCode > 0L) { "Host version code must be positive" }

        val device = root.objectValue("device")
        device.requireExactKeys("sdkInt", "release", "manufacturer", "brand", "model", "supportedAbis")
        val sdkInt = device.long("sdkInt")
        require(sdkInt in 1L..1_000L) { "Android API level is invalid" }
        val release = device.string("release")
        val manufacturer = device.string("manufacturer")
        val brand = device.string("brand")
        val model = device.string("model")
        listOf(release, manufacturer, brand, model).forEach {
            requireSafeText(it, "Device snapshot text")
        }
        val supportedAbis = device.array("supportedAbis").values.mapIndexed { index, value ->
            value.asString("ABI $index").also {
                requireSafeText(it, "Device ABI", allowEmpty = false)
                require(it.toByteArray(StandardCharsets.UTF_8).size <= 128) { "Device ABI is too long" }
            }
        }
        require(supportedAbis.size in 1..MAX_ABIS && supportedAbis.distinct().size == supportedAbis.size) {
            "Device ABI snapshot is empty, duplicated, or too large"
        }

        return ValidatedHostCapabilitySnapshot(
            executionId = executionId,
            entryPoint = entryPoint,
            projectFilesAvailable = project,
            grants = grants.toSet(),
            packageName = packageName,
            versionName = versionName,
            versionCode = versionCode,
            debuggable = app.boolean("debuggable"),
            sdkInt = sdkInt.toInt(),
            release = release,
            manufacturer = manufacturer,
            brand = brand,
            model = model,
            supportedAbis = supportedAbis,
        )
    }

    private fun decodeUtf8(encoded: ByteArray): String = try {
        val decoded = StandardCharsets.UTF_8.newDecoder()
            .onMalformedInput(CodingErrorAction.REPORT)
            .onUnmappableCharacter(CodingErrorAction.REPORT)
            .decode(ByteBuffer.wrap(encoded))
        decoded.toString()
    } catch (error: Exception) {
        throw IllegalArgumentException("Host capability snapshot is not valid UTF-8", error)
    }

    private fun requireSafeText(value: String, label: String, allowEmpty: Boolean = true) {
        require(allowEmpty || value.isNotEmpty()) { "$label is empty" }
        require(value.toByteArray(StandardCharsets.UTF_8).size <= MAX_TEXT_BYTES) { "$label is too long" }
        require(value.none(Character::isISOControl)) { "$label contains control characters" }
    }
}

private sealed interface JsonValue {
    fun asObject(label: String): JsonObject = this as? JsonObject
        ?: throw IllegalArgumentException("$label must be an object")

    fun asString(label: String): String = (this as? JsonString)?.value
        ?: throw IllegalArgumentException("$label must be a string")
}

private data class JsonObject(val values: LinkedHashMap<String, JsonValue>) : JsonValue {
    fun requireExactKeys(vararg expected: String) {
        require(values.keys == expected.toSet()) { "JSON object fields are missing or unsupported" }
    }

    fun objectValue(name: String): JsonObject = required(name).asObject(name)

    fun array(name: String): JsonArray = required(name) as? JsonArray
        ?: throw IllegalArgumentException("$name must be an array")

    fun string(name: String): String = required(name).asString(name)

    fun long(name: String): Long = (required(name) as? JsonInteger)?.value
        ?: throw IllegalArgumentException("$name must be an integer")

    fun boolean(name: String): Boolean = (required(name) as? JsonBoolean)?.value
        ?: throw IllegalArgumentException("$name must be a boolean")

    private fun required(name: String): JsonValue = requireNotNull(values[name]) { "$name is missing" }
}

private data class JsonArray(val values: List<JsonValue>) : JsonValue
private data class JsonString(val value: String) : JsonValue
private data class JsonInteger(val value: Long) : JsonValue
private data class JsonBoolean(val value: Boolean) : JsonValue
private object JsonNull : JsonValue

/** Minimal strict JSON reader: duplicate keys, invalid escapes/numbers and trailing data fail closed. */
private class StrictJsonParser(private val input: String) {
    private var index = 0
    private var nodes = 0

    fun parse(): JsonValue {
        skipWhitespace()
        val value = parseValue(0)
        skipWhitespace()
        require(index == input.length) { "Host capability snapshot contains trailing JSON data" }
        return value
    }

    private fun parseValue(depth: Int): JsonValue {
        require(depth <= 16) { "Host capability snapshot JSON is too deeply nested" }
        require(++nodes <= 512) { "Host capability snapshot JSON has too many values" }
        skipWhitespace()
        require(index < input.length) { "Host capability snapshot JSON is truncated" }
        return when (input[index]) {
            '{' -> parseObject(depth + 1)
            '[' -> parseArray(depth + 1)
            '"' -> JsonString(parseString())
            't' -> parseLiteral("true", JsonBoolean(true))
            'f' -> parseLiteral("false", JsonBoolean(false))
            'n' -> parseLiteral("null", JsonNull)
            '-', in '0'..'9' -> JsonInteger(parseInteger())
            else -> throw IllegalArgumentException("Host capability snapshot contains invalid JSON")
        }
    }

    private fun parseObject(depth: Int): JsonObject {
        expect('{')
        skipWhitespace()
        val values = LinkedHashMap<String, JsonValue>()
        if (take('}')) return JsonObject(values)
        while (true) {
            skipWhitespace()
            require(index < input.length && input[index] == '"') { "JSON object key must be a string" }
            val key = parseString()
            require(values.putIfAbsent(key, JsonNull) == null) { "JSON object contains a duplicate key" }
            skipWhitespace()
            expect(':')
            values[key] = parseValue(depth)
            skipWhitespace()
            if (take('}')) return JsonObject(values)
            expect(',')
        }
    }

    private fun parseArray(depth: Int): JsonArray {
        expect('[')
        skipWhitespace()
        val values = ArrayList<JsonValue>()
        if (take(']')) return JsonArray(values)
        while (true) {
            values += parseValue(depth)
            skipWhitespace()
            if (take(']')) return JsonArray(values)
            expect(',')
        }
    }

    private fun parseString(): String {
        expect('"')
        val output = StringBuilder()
        while (index < input.length) {
            val character = input[index++]
            when {
                character == '"' -> {
                    requireValidSurrogates(output)
                    return output.toString()
                }
                character == '\\' -> {
                    require(index < input.length) { "JSON escape is truncated" }
                    when (val escaped = input[index++]) {
                        '"', '\\', '/' -> output.append(escaped)
                        'b' -> output.append('\b')
                        'f' -> output.append('\u000c')
                        'n' -> output.append('\n')
                        'r' -> output.append('\r')
                        't' -> output.append('\t')
                        'u' -> output.append(parseUnicodeEscape())
                        else -> throw IllegalArgumentException("JSON string contains an invalid escape")
                    }
                }
                character.code < 0x20 -> throw IllegalArgumentException("JSON string contains a control character")
                else -> output.append(character)
            }
        }
        throw IllegalArgumentException("JSON string is unterminated")
    }

    private fun parseUnicodeEscape(): Char {
        require(index + 4 <= input.length) { "JSON Unicode escape is truncated" }
        val value = input.substring(index, index + 4).toIntOrNull(16)
            ?: throw IllegalArgumentException("JSON Unicode escape is invalid")
        index += 4
        return value.toChar()
    }

    private fun parseInteger(): Long {
        val start = index
        if (take('-')) require(index < input.length) { "JSON number is truncated" }
        when {
            take('0') -> require(index >= input.length || input[index] !in '0'..'9') {
                "JSON number contains a leading zero"
            }
            index < input.length && input[index] in '1'..'9' -> {
                index++
                while (index < input.length && input[index] in '0'..'9') index++
            }
            else -> throw IllegalArgumentException("JSON number is invalid")
        }
        require(index >= input.length || input[index] !in charArrayOf('.', 'e', 'E')) {
            "Host capability snapshot permits integers only"
        }
        return input.substring(start, index).toLongOrNull()
            ?: throw IllegalArgumentException("JSON integer is out of range")
    }

    private fun <T : JsonValue> parseLiteral(literal: String, value: T): T {
        require(input.regionMatches(index, literal, 0, literal.length)) { "JSON literal is invalid" }
        index += literal.length
        return value
    }

    private fun requireValidSurrogates(value: CharSequence) {
        var cursor = 0
        while (cursor < value.length) {
            val character = value[cursor]
            when {
                Character.isHighSurrogate(character) -> {
                    require(cursor + 1 < value.length && Character.isLowSurrogate(value[cursor + 1])) {
                        "JSON string contains an unpaired surrogate"
                    }
                    cursor += 2
                }
                Character.isLowSurrogate(character) ->
                    throw IllegalArgumentException("JSON string contains an unpaired surrogate")
                else -> cursor++
            }
        }
    }

    private fun skipWhitespace() {
        while (index < input.length && input[index] in charArrayOf(' ', '\t', '\r', '\n')) index++
    }

    private fun expect(character: Char) {
        require(take(character)) { "Expected '$character' in host capability snapshot JSON" }
    }

    private fun take(character: Char): Boolean {
        if (index >= input.length || input[index] != character) return false
        index++
        return true
    }
}
