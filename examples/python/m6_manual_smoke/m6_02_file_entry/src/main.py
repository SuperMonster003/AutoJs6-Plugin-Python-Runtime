from __future__ import annotations

import sys
from pathlib import Path

import root_helper
import sibling_helper
from autojs6 import result


print("M6-02-FILE-ENTRY-BEGIN")
project_root = Path.cwd().resolve()
entry_file = Path(__file__).resolve()
checks = {
    "entryDirectoryImport": sibling_helper.VALUE == "entry-directory-import-ok",
    "projectRootFallback": root_helper.VALUE == "project-root-fallback-ok",
    "cwdIsProjectRoot": entry_file.parent.parent == project_root,
    "pathZeroIsEntryDirectory": Path(sys.path[0]).resolve() == entry_file.parent,
    "logicalFile": __file__.replace("\\", "/") == "src/main.py",
    "logicalArgv": sys.argv[0].replace("\\", "/") == "src/main.py",
    "fileModeSpec": __spec__ is None,
}
failures = sorted(name for name, passed in checks.items() if not passed)
if failures:
    raise AssertionError("M6-02 file-entry failed checks: " + ", ".join(failures))

print("M6-02-FILE-ENTRY-PASS")
result.set({"case": "M6-02-FILE", "allChecks": True, "entryMode": "file"})
