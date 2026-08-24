package io.github.supermonster003.autojs6.plugin.python.runtime.service

import org.autojs.plugin.python.runtime.api.PythonExecutionHeartbeat
import org.autojs.plugin.python.runtime.api.PythonRequestId
import org.autojs.plugin.python.runtime.api.PythonRuntimeValidation

/** Pure ordered heartbeat producer; scheduling and Binder delivery remain session-owned. */
internal class PythonHeartbeatPolicy(
    private val requestId: PythonRequestId,
    private val createdAtMillis: Long,
) {
    private var nextSequence = 1L
    private var lastNowMillis = createdAtMillis

    init {
        require(createdAtMillis >= 0L)
    }

    @Synchronized
    fun next(nowMillis: Long): PythonExecutionHeartbeat {
        require(nowMillis >= lastNowMillis) { "Heartbeat clock moved backwards" }
        check(nextSequence < Long.MAX_VALUE) { "Heartbeat sequence is exhausted" }
        return PythonExecutionHeartbeat(
            requestId = requestId,
            sequence = nextSequence++,
            elapsedMillis = nowMillis - createdAtMillis,
        ).also(PythonRuntimeValidation::validateHeartbeat).also {
            lastNowMillis = nowMillis
        }
    }
}
