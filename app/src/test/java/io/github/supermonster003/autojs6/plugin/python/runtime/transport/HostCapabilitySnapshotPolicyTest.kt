package io.github.supermonster003.autojs6.plugin.python.runtime.transport

import org.junit.Assert.assertEquals
import org.junit.Assert.assertFalse
import org.junit.Assert.assertTrue
import org.junit.Assert.fail
import org.junit.Test

class HostCapabilitySnapshotPolicyTest {
    @Test
    fun exactExecutionBoundSnapshotIsAccepted() {
        val validated = HostCapabilitySnapshotPolicy.validate(
            encoded = snapshot(project = true),
            expectedExecutionId = EXECUTION_ID,
            expectedEntryPoint = "main.py",
            expectedProjectFilesAvailable = true,
        )

        assertEquals(EXECUTION_ID, validated.executionId)
        assertEquals("main.py", validated.entryPoint)
        assertTrue(validated.projectFilesAvailable)
        assertEquals(
            setOf("app.snapshot.read", "device.snapshot.read", "project.files.read"),
            validated.grants,
        )
        assertEquals("org.autojs.autojs6", validated.packageName)
        assertEquals(31, validated.sdkInt)
        assertEquals(listOf("arm64-v8a"), validated.supportedAbis)
    }

    @Test
    fun standaloneSnapshotOmitsProjectGrant() {
        val validated = HostCapabilitySnapshotPolicy.validate(
            encoded = snapshot(project = false),
            expectedExecutionId = EXECUTION_ID,
            expectedEntryPoint = "main.py",
            expectedProjectFilesAvailable = false,
        )

        assertFalse(validated.projectFilesAvailable)
        assertEquals(setOf("app.snapshot.read", "device.snapshot.read"), validated.grants)
    }

    @Test
    fun correlationWorkspaceAndGrantDriftFailClosed() {
        rejected {
            HostCapabilitySnapshotPolicy.validate(snapshot(), "other", "main.py", true)
        }
        rejected {
            HostCapabilitySnapshotPolicy.validate(snapshot(), EXECUTION_ID, "other.py", true)
        }
        rejected {
            HostCapabilitySnapshotPolicy.validate(snapshot(), EXECUTION_ID, "main.py", false)
        }
        rejected {
            HostCapabilitySnapshotPolicy.validate(
                snapshotText().replace(
                    "\"project.files.read\"",
                    "\"shell.exec\"",
                ).toByteArray(),
                EXECUTION_ID,
                "main.py",
                true,
            )
        }
    }

    @Test
    fun malformedDuplicateAndTrailingJsonFailClosed() {
        rejected {
            HostCapabilitySnapshotPolicy.validate(
                snapshotText().replace("\"schemaVersion\":1", "\"schemaVersion\":1,\"schemaVersion\":1")
                    .toByteArray(),
                EXECUTION_ID,
                "main.py",
                true,
            )
        }
        rejected {
            HostCapabilitySnapshotPolicy.validate(
                (snapshotText() + "{}").toByteArray(),
                EXECUTION_ID,
                "main.py",
                true,
            )
        }
        rejected {
            HostCapabilitySnapshotPolicy.validate(
                byteArrayOf(0xc3.toByte(), 0x28),
                EXECUTION_ID,
                "main.py",
                true,
            )
        }
    }

    private fun snapshot(project: Boolean = true): ByteArray = snapshotText(project).toByteArray()

    private fun snapshotText(project: Boolean = true): String {
        val grants = if (project) {
            "\"app.snapshot.read\",\"device.snapshot.read\",\"project.files.read\""
        } else {
            "\"app.snapshot.read\",\"device.snapshot.read\""
        }
        return (
            "{" +
                "\"schemaVersion\":1," +
                "\"execution\":{" +
                "\"id\":\"$EXECUTION_ID\"," +
                "\"entryPoint\":\"main.py\"," +
                "\"project\":$project}," +
                "\"grants\":[$grants]," +
                "\"app\":{" +
                "\"packageName\":\"org.autojs.autojs6\"," +
                "\"versionName\":\"preview\"," +
                "\"versionCode\":1," +
                "\"debuggable\":true}," +
                "\"device\":{" +
                "\"sdkInt\":31," +
                "\"release\":\"12\"," +
                "\"manufacturer\":\"example\"," +
                "\"brand\":\"example\"," +
                "\"model\":\"device\"," +
                "\"supportedAbis\":[\"arm64-v8a\"]}}"
            )
    }

    private fun rejected(block: () -> Unit) {
        try {
            block()
            fail("Expected host capability snapshot to be rejected")
        } catch (_: IllegalArgumentException) {
            // Expected.
        }
    }

    private companion object {
        const val EXECUTION_ID = "12345678-1234-4234-8234-1234567890ab"
    }
}
