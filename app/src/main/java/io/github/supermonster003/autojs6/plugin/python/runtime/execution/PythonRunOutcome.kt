package io.github.supermonster003.autojs6.plugin.python.runtime.execution

import org.autojs.plugin.python.runtime.api.PythonOutputStream
import org.autojs.plugin.python.runtime.api.PythonTracebackFrame

internal data class BufferedOutputRecord(
    val stream: PythonOutputStream,
    val bytes: ByteArray,
)

internal sealed interface PythonRunOutcome {
    val output: List<BufferedOutputRecord>

    data class Completed(
        val exitCode: Int,
        val structuredJson: String?,
        val artifactPaths: List<String>,
        override val output: List<BufferedOutputRecord>,
    ) : PythonRunOutcome

    data class Failed(
        val exceptionType: String,
        val exceptionMessage: String,
        val traceback: List<PythonTracebackFrame>,
        override val output: List<BufferedOutputRecord>,
    ) : PythonRunOutcome

    data class OutputLimitExceeded(
        override val output: List<BufferedOutputRecord>,
    ) : PythonRunOutcome

    data object Stopped : PythonRunOutcome {
        override val output: List<BufferedOutputRecord> = emptyList()
    }
}
