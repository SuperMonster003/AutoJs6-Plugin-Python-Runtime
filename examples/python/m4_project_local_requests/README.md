# Project-local `requests` example

This project demonstrates M4 Path A: pure-Python distributions live beside the
project source and travel in the same bounded workspace snapshot. AutoJs6 does
not run `pip` on Android and does not download missing imports.

From this directory on a development machine with Python and pip, install the
pinned pure wheels directly into the project root:

```powershell
python -m pip install --requirement requirements.txt --target . --no-compile --only-binary=:all: --platform any --implementation py --python-version 3.13 --abi none
```

Run that command in a clean copy of this example. If pip creates a `bin`
directory for desktop console launchers, inspect and remove that generated
directory; Android does not use it. Verify that the resulting tree contains no
`.so`, `.pyd`, `.dll`, `.dylib`, or `.exe` files, then copy the whole directory
to AutoJs6 and run it as a Python project. `main.py` verifies that `requests`
came from the project, performs an HTTPS GET, and publishes a strict JSON
result containing the response and dependency versions.

Generated dependency directories are intentionally not committed here. See
[`docs/python/PROJECT_LOCAL_PACKAGES.md`](../../../docs/python/PROJECT_LOCAL_PACKAGES.md)
for the supported layout, capacity limits, reproducibility guidance, and
failure behavior.
