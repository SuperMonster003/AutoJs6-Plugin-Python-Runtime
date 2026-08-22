package io.github.supermonster003.autojs6.plugin.python.runtime.execution

import android.content.Context
import com.chaquo.python.PyObject
import com.chaquo.python.Python
import com.chaquo.python.android.AndroidPlatform
import org.autojs.plugin.python.runtime.api.PythonEntryMode
import org.autojs.plugin.python.runtime.api.PythonExecutionRequest
import org.autojs.plugin.python.runtime.api.PythonInputEcho
import org.autojs.plugin.python.runtime.api.PythonInputReply
import org.autojs.plugin.python.runtime.api.PythonOutputStream
import org.autojs.plugin.python.runtime.api.PythonTracebackFrame
import org.autojs.plugin.python.runtime.api.PythonTracebackOrigin
import java.io.File

/**
 * Process-local CPython facade. User code receives strings, numbers and bytes only: no Context,
 * Binder, ScriptRuntime or callback object crosses into its globals. Chaquopy's own Java bridge
 * remains available to Python and is therefore an explicit non-sandbox boundary of this POC.
 */
internal class ChaquopyRuntime(context: Context) {
    private val applicationContext = context.applicationContext
    private val startLock = Any()
    val workspaceParentDirectory = File(applicationContext.cacheDir, "python-runtime-workspaces")
    val outputArtifactParentDirectory = File(applicationContext.cacheDir, "python-runtime-results")

    fun prepare() {
        ensureStarted()
    }

    fun execute(
        source: ByteArray,
        request: PythonExecutionRequest,
        workspaceRoot: File? = null,
        hostCapabilitySnapshot: ByteArray? = null,
        stdinSnapshot: ByteArray? = null,
        onOutput: (BufferedOutputRecord) -> Unit,
        onInput: ((String, PythonInputEcho) -> PythonInputReply)? = null,
        outputArtifactRoot: File? = null,
    ): PythonRunOutcome {
        val python = ensureStarted()
        val bootstrap = python.getModule("autojs6_runtime.bootstrap")
        val outputSink = ChaquopyOutputSink(onOutput)
        val inputBridge = onInput?.let(::ChaquopyInputBridge)
        val result = if (workspaceRoot == null) {
            bootstrap.callAttr(
                "run_source",
                source,
                request.entryPoint,
                request.arguments.toTypedArray(),
                request.maxOutputBytes,
                request.maxOutputChunkBytes,
                request.maxOutputChunks,
                hostCapabilitySnapshot ?: EMPTY_CAPABILITY_SNAPSHOT,
                stdinSnapshot ?: EMPTY_STDIN_SNAPSHOT,
                outputSink,
                inputBridge,
                outputArtifactRoot?.absolutePath,
                request.resultPolicy?.maxStructuredJsonBytes ?: 0,
                request.resultPolicy?.maxArtifacts ?: 0,
                request.resultPolicy?.maxArtifactPathBytes ?: 0,
            )
        } else {
            bootstrap.callAttr(
                "run_project",
                source,
                request.entryPoint,
                workspaceRoot.absolutePath,
                request.arguments.toTypedArray(),
                request.maxOutputBytes,
                request.maxOutputChunkBytes,
                request.maxOutputChunks,
                hostCapabilitySnapshot ?: EMPTY_CAPABILITY_SNAPSHOT,
                stdinSnapshot ?: EMPTY_STDIN_SNAPSHOT,
                outputSink,
                request.entryMode.bootstrapName(),
                inputBridge,
                outputArtifactRoot?.absolutePath,
                request.resultPolicy?.maxStructuredJsonBytes ?: 0,
                request.resultPolicy?.maxArtifacts ?: 0,
                request.resultPolicy?.maxArtifactPathBytes ?: 0,
            )
        }
        return try {
            inputBridge?.rethrowFailure()
            outputSink.rethrowFailure()
            decodeOutcome(result).also { outcome ->
                require(outcome.output.isEmpty()) {
                    "Python streaming bootstrap returned buffered output"
                }
            }
        } finally {
            result.close()
        }
    }

    private fun ensureStarted(): Python = synchronized(startLock) {
        if (!Python.isStarted()) Python.start(AndroidPlatform(applicationContext))
        Python.getInstance()
    }

    private fun decodeOutcome(result: PyObject): PythonRunOutcome {
        val output = required(result, "output").asList().map(::decodeOutputRecord)
        return when (required(result, "status").toString()) {
            "completed" -> PythonRunOutcome.Completed(
                exitCode = required(result, "exit_code").toInt(),
                structuredJson = nullable(result, "structured_json")?.toJava(String::class.java),
                artifactPaths = required(result, "artifact_paths").asList().map(PyObject::toString),
                output = output,
            )
            "failed" -> PythonRunOutcome.Failed(
                exceptionType = boundedNonBlank(
                    required(result, "exception_type").toString(),
                    MAX_EXCEPTION_TYPE_BYTES,
                    "PythonError",
                ),
                exceptionMessage = boundedUtf8(
                    required(result, "exception_message").toString(),
                    MAX_EXCEPTION_MESSAGE_BYTES,
                ),
                traceback = required(result, "traceback").asList()
                    .take(MAX_WIRE_TRACEBACK_FRAMES)
                    .map(::decodeTracebackFrame),
                output = output,
            )
            "output_limit" -> PythonRunOutcome.OutputLimitExceeded(output)
            "stopped" -> PythonRunOutcome.Stopped
            else -> error("Python bootstrap returned an unknown outcome")
        }
    }

    private fun decodeOutputRecord(value: PyObject): BufferedOutputRecord {
        val fields = value.asList()
        require(fields.size == 2) { "Python bootstrap returned a malformed output record" }
        val stream = when (fields[0].toString()) {
            "stdout" -> PythonOutputStream.STDOUT
            "stderr" -> PythonOutputStream.STDERR
            else -> error("Python bootstrap returned an unknown output stream")
        }
        val bytes = fields[1].toJava(ByteArray::class.java)
        require(bytes.isNotEmpty()) { "Python bootstrap returned an empty output chunk" }
        return BufferedOutputRecord(stream, bytes.copyOf())
    }

    private fun decodeTracebackFrame(value: PyObject): PythonTracebackFrame {
        val origin = when (required(value, "origin").toString()) {
            "project" -> PythonTracebackOrigin.PROJECT
            "stdlib" -> PythonTracebackOrigin.STDLIB
            "package" -> PythonTracebackOrigin.PACKAGE
            "generated" -> PythonTracebackOrigin.GENERATED
            else -> error("Python bootstrap returned an unknown traceback origin")
        }
        val sourceLineObject = field(value, "source_line")
        val fileName = if (origin == PythonTracebackOrigin.GENERATED) {
            "<generated>"
        } else {
            boundedNonBlank(required(value, "file_name").toString(), MAX_FRAME_FIELD_BYTES, "module.py")
        }
        return PythonTracebackFrame(
            origin = origin,
            fileName = fileName,
            lineNumber = required(value, "line_number").toInt().coerceAtLeast(1),
            functionName = boundedNonBlank(
                required(value, "function_name").toString(),
                MAX_FRAME_FIELD_BYTES,
                "<module>",
            ),
            sourceLine = sourceLineObject?.toString()
                ?.let { boundedUtf8(it, MAX_FRAME_FIELD_BYTES) },
        )
    }

    private fun required(value: PyObject, key: String): PyObject =
        requireNotNull(nullable(value, key)) { "Python bootstrap result field '$key' must not be null" }

    private fun nullable(value: PyObject, key: String): PyObject? {
        val fields = value.asMap()
        val pythonKey = PyObject.fromJava(key)
        require(fields.containsKey(pythonKey)) { "Python bootstrap result is missing '$key'" }
        return fields[pythonKey]
    }

    private fun field(value: PyObject, key: String): PyObject? =
        value.asMap()[PyObject.fromJava(key)]

    private fun boundedNonBlank(value: String, maximumBytes: Int, fallback: String): String =
        boundedUtf8(value, maximumBytes).takeUnless(String::isBlank) ?: fallback

    private fun boundedUtf8(value: String, maximumBytes: Int): String {
        if (value.toByteArray(Charsets.UTF_8).size <= maximumBytes) return value
        val output = StringBuilder(minOf(value.length, maximumBytes))
        var usedBytes = 0
        val codePoints = value.codePoints().iterator()
        while (codePoints.hasNext()) {
            val text = String(Character.toChars(codePoints.nextInt()))
            val size = text.toByteArray(Charsets.UTF_8).size
            if (usedBytes + size > maximumBytes) break
            output.append(text)
            usedBytes += size
        }
        return output.toString()
    }

    private companion object {
        const val MAX_WIRE_TRACEBACK_FRAMES = 32
        const val MAX_FRAME_FIELD_BYTES = 1024
        const val MAX_EXCEPTION_TYPE_BYTES = 1024
        const val MAX_EXCEPTION_MESSAGE_BYTES = 4096
        val EMPTY_CAPABILITY_SNAPSHOT = ByteArray(0)
        val EMPTY_STDIN_SNAPSHOT = ByteArray(0)
    }
}

private fun PythonEntryMode.bootstrapName(): String = when (this) {
    PythonEntryMode.FILE -> "file"
    PythonEntryMode.MODULE -> "module"
}
