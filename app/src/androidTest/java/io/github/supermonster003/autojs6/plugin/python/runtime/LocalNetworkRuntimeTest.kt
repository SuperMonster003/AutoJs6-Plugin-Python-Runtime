package io.github.supermonster003.autojs6.plugin.python.runtime

import androidx.test.ext.junit.runners.AndroidJUnit4
import androidx.test.platform.app.InstrumentationRegistry
import io.github.supermonster003.autojs6.plugin.python.runtime.execution.ChaquopyRuntime
import io.github.supermonster003.autojs6.plugin.python.runtime.execution.PythonRunOutcome
import org.autojs.plugin.python.runtime.api.*
import org.junit.Assert.*
import org.junit.Assume.assumeTrue
import org.junit.Test
import org.junit.runner.RunWith

@RunWith(AndroidJUnit4::class)
class LocalNetworkRuntimeTest {
    @Test fun localNetworkUsesThePluginGrant() {
        val args = InstrumentationRegistry.getArguments()
        assumeTrue("Provide lanPort for the owned LAN fixture", args.containsKey("lanPort"))
        val context = InstrumentationRegistry.getInstrumentation().targetContext
        val host = org.json.JSONObject.quote(args.getString("lanHost", "10.0.2.2"))
        val port = requireNotNull(args.getString("lanPort")).toInt()
        val source = "import socket\nwith socket.create_connection(($host, $port), 3) as s:\n    assert s.recv(1) == b'K'\n".toByteArray()
        val request = PythonExecutionRequest(
            requestId = PythonRequestId.fromBytes(ByteArray(16) { 37 }),
            protocolVersion = PythonRuntimeMetadata.protocolVersion,
            entryPoint = "network.py",
            source = PythonPayloadReference(PythonPayloadKind.SOURCE, 0, source.size.toLong(), PythonSha256.digest(source)),
            timeoutMillis = 10_000L, maxOutputBytes = 4096L, maxOutputChunkBytes = 1024, maxOutputChunks = 8L,
        )
        val result = ChaquopyRuntime(context).execute(source, request, onOutput = {})
        if (LocalNetworkAccess.isGranted(context)) assertTrue(result.toString(), result is PythonRunOutcome.Completed)
        else {
            assertTrue(result.toString(), result is PythonRunOutcome.Failed)
            assertTrue((result as PythonRunOutcome.Failed).exceptionMessage,
                result.exceptionMessage.contains(context.getString(R.string.local_network_failure_hint)))
        }
    }
}
