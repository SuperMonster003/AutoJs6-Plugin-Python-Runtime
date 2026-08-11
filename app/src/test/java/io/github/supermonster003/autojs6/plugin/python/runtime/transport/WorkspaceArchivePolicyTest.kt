package io.github.supermonster003.autojs6.plugin.python.runtime.transport

import org.junit.Assert.assertEquals
import org.junit.Assert.fail
import org.junit.Test

class WorkspaceArchivePolicyTest {
    @Test
    fun normalizedRelativeFilesAndDirectoriesAreAccepted() {
        assertEquals(
            WorkspaceArchiveEntryPath("pkg", true),
            normalizeArchiveEntry("pkg/", true),
        )
        assertEquals(
            WorkspaceArchiveEntryPath("pkg/helper.py", false),
            normalizeArchiveEntry("pkg/helper.py", false),
        )

        WorkspaceArchivePathPolicy("src/main.py").apply {
            accept("src", true)
            accept("src/helper.py", false)
            accept("data/value.txt", false)
        }
    }

    @Test
    fun unsafeAndPlatformDependentNamesAreRejected() {
        listOf(
            "/absolute.py",
            "C:drive.py",
            "C:/drive.py",
            "//unc/share.py",
            "dir\\file.py",
            "dir//file.py",
            "dir/./file.py",
            "dir/../file.py",
            "nul\u0000file.py",
        ).forEach { name -> rejected { normalizeArchiveEntry(name, false) } }
    }

    @Test
    fun duplicateAndCaseFoldAliasesAreRejected() {
        WorkspaceArchivePathPolicy("main.py").apply {
            accept("pkg/helper.py", false)
            rejected { accept("PKG/HELPER.PY", false) }
        }
        WorkspaceArchivePathPolicy("main.py").apply {
            accept("Pkg/first.py", false)
            rejected { accept("pkg/second.py", false) }
        }
    }

    @Test
    fun fileDirectoryPrefixConflictsAreRejectedInEitherOrder() {
        WorkspaceArchivePathPolicy("main.py").apply {
            accept("pkg", false)
            rejected { accept("pkg/helper.py", false) }
        }
        WorkspaceArchivePathPolicy("main.py").apply {
            accept("pkg/helper.py", false)
            rejected { accept("pkg", false) }
        }
    }

    @Test
    fun archiveCannotContainOrShadowSeparateSourceEntry() {
        listOf(
            "src/main.py" to false,
            "SRC/MAIN.PY" to false,
            "src/main.py/cache" to false,
            "src" to false,
            "SRC/helper.py" to false,
        ).forEach { (path, directory) ->
            rejected { WorkspaceArchivePathPolicy("src/main.py").accept(path, directory) }
        }

        WorkspaceArchivePathPolicy("src/main.py").accept("src", true)
    }

    private fun rejected(block: () -> Unit) {
        try {
            block()
            fail("Expected workspace archive input to be rejected")
        } catch (_: IllegalArgumentException) {
            // Expected.
        }
    }
}
