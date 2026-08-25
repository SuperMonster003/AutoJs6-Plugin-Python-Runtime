from __future__ import annotations

import sys
from importlib.metadata import version
from pathlib import Path

import plain_module
import vendored_probe
from autojs6 import result

from . import cycle_a, cycle_b, stateful
from .package_api import package_value
from .relative_helper import RELATIVE_VALUE


print("M6-02-IMPORTS-BEGIN")
entry_file = Path(__file__).resolve()
project_root = entry_file.parents[1]
state_counter = stateful.claim_first_import()
dependency_version = version("vendored-probe")

checks = {
    "fileImport": plain_module.VALUE == "file-import-ok",
    "packageImport": package_value() == "package-import-ok",
    "relativeImport": RELATIVE_VALUE == "relative-import-ok",
    "circularImport": cycle_a.chain() == "AB" and cycle_b.sees_a() == "A",
    "moduleName": __name__ == "__main__",
    "modulePackage": __package__ == "smoke_imports",
    "moduleSpec": __spec__ is not None and __spec__.name == "smoke_imports.main",
    "moduleArgv": Path(sys.argv[0]).resolve() == entry_file,
    "executionRoot": Path(sys.path[0]).resolve() == project_root,
    "projectLocalDependency": vendored_probe.fetch() == "project-local-package",
    "distributionMetadata": dependency_version == "1.2.3",
    "freshState": state_counter == 1,
}
failures = sorted(name for name, passed in checks.items() if not passed)
if failures:
    raise AssertionError("M6-02 failed checks: " + ", ".join(failures))

print("M6-02-IMPORTS-PASS")
result.set(
    {
        "case": "M6-02",
        "allChecks": True,
        "module": __spec__.name,
        "package": __package__,
        "stateCounter": state_counter,
        "dependencyVersion": dependency_version,
        "circular": cycle_a.chain() + "/" + cycle_b.sees_a(),
    }
)
