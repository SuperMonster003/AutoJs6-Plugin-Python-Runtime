# Project-local pure-Python packages

Status: supported by M4 Path A for admitted Python projects.

AutoJs6 Python projects may carry pure-Python packages in the project root.
The Host snapshots the complete admitted project, the Plugin extracts that
bounded snapshot, and project execution places the extracted project root at
the front of `sys.path`. Normal package imports, transitive imports, namespace
packages, and `.dist-info` metadata therefore work without a new protocol or a
runtime package installer.

This feature does not make Android run `pip`. It never resolves a missing
import, downloads code, or mutates the source project. Dependency preparation
is an explicit development-machine step, and the resulting files execute with
the same trust and permissions as the rest of the selected script.
It does not make hostile Python a security sandbox.

## Supported layout

Install packages directly into the directory which contains `project.json`:

```text
my-python-project/
|-- project.json
|-- main.py
|-- requirements.txt
|-- requests/
|-- requests-2.34.2.dist-info/
|-- urllib3/
|-- urllib3-2.7.0.dist-info/
`-- ...
```

The minimal declaration remains ordinary project metadata:

```json
{
  "type": "python",
  "main": "main.py",
  "timeout": 120000
}
```

The project root is already the Python import root. Do not add machine-local
absolute paths to `sys.path`, and do not rely on a desktop virtual environment
which is outside the copied project.

## Preparing a reproducible pure-Python tree

Pin the complete intended dependency set in `requirements.txt`, then use only
platform-independent wheels:

```powershell
python -m pip install --requirement requirements.txt --target . --no-compile --only-binary=:all: --platform any --implementation py --python-version 3.13 --abi none
```

Run this in a clean staging copy of the project. Some desktop pip builds create
a `bin` directory containing console launchers; inspect and remove that
generated directory before copying the project to Android. It is not used by
package imports.

The important constraints are:

- `--target .` puts imports and distribution metadata in the project root;
- `--only-binary=:all:` refuses source distributions and build steps;
- `--platform any --implementation py --abi none` selects only portable Python
  wheels rather than desktop native extensions;
- `--python-version 3.13` resolves against the packaged CPython line;
- `--no-compile` avoids shipping development-machine bytecode caches.

After installation, reject the tree if it contains `.so`, `.pyd`, `.dll`,
`.dylib`, or `.exe` files. A wheel being downloadable on a desktop does not
imply that a native extension supports Android, the device ABI, or its page
size. Native packages remain a separate M4 Path C task.

For repeatable builds, keep exact versions, retain the wheel files in a trusted
offline wheelhouse, record hashes with `pip hash`, and install with
`--require-hashes --no-index --find-links <wheelhouse>`. Review each package's
license before distributing the project. Never treat project-local packages as
trusted merely because they are pure Python.

## Capacity and admission

One project workspace is bounded by all three limits:

| Dimension | Limit |
| --- | ---: |
| Compressed workspace ZIP | 64 MiB |
| Archive file entries | 8192 |
| Total extracted file bytes | 128 MiB |

The Host enforces these limits while constructing the immutable snapshot. It
also passes the snapshot's actual compressed length, entry count, and expanded
length into Provider selection. A Provider which advertises less capacity is
rejected before dispatch instead of receiving a payload it cannot admit.

Exceeding a Host snapshot bound fails with
`PYTHON_RUNTIME_WORKSPACE_INVALID`. Selecting an older or otherwise undersized
Provider fails as `PYTHON_RUNTIME_PROVIDER_INCOMPATIBLE`. Missing dependencies
still raise the ordinary Python `ModuleNotFoundError`; none of these paths
trigger a fallback engine or an online install.

The workspace limits cover every non-entry project file, not only package
files; the declared entry source uses its separate 4 MiB SOURCE bound. Remove
tests, documentation, wheel archives, caches, and build output which are not
needed at runtime. Do not include secrets: the whole admitted project crosses
the Host-to-Plugin boundary as one read-only execution snapshot.

## Worked example

[`examples/python/m4_project_local_requests`](../../examples/python/m4_project_local_requests)
pins `requests` and its pure-Python dependency closure. After installing the
requirements into that example directory, copy the whole directory to AutoJs6
and run the project. The script proves that `requests` was imported from the
project root, performs an HTTPS request, and publishes dependency versions in
the structured result.
