# Third-Party Notices

This distribution includes or is built with the third-party runtime components
identified below. This notice is a concise attribution and source pointer; the
applicable upstream license text controls.

Verbatim upstream license copies are checked into and packaged from
`app/src/main/assets/third_party_licenses/`. In the installed APK asset
namespace they are available under `third_party_licenses/`.

## Chaquopy 17.0.0

- Component: Chaquopy, including its Android Python runtime integration.
- License: MIT License.
- Upstream project: https://chaquo.com/chaquopy/
- Upstream source: https://github.com/chaquo/chaquopy
- Attribution: upstream developer metadata names Malcolm Smith. Copyright in
  Chaquopy remains with its upstream authors and contributors.

The exact resolved Chaquopy 17.0.0 artifacts and their SHA-256 values are
recorded in `locks/python-runtime.lock` and `gradle/verification-metadata.xml`.
The full MIT text is packaged as
`third_party_licenses/Chaquopy-17.0.0-LICENSE.txt`.

## CPython 3.13 / 3.13.9

- Component: CPython 3.13; the pinned packaged runtime is CPython 3.13.9.
- License: Python Software Foundation License Version 2 (recorded as
  `PSF-2.0` in the runtime lock), together with the historical licenses and
  notices incorporated by CPython.
- Upstream source for the pinned version:
  https://github.com/python/cpython/tree/v3.13.9
- Upstream license and copyright history:
  https://docs.python.org/3.13/license.html
- Attribution: copyright is held by the Python Software Foundation and the
  historical contributors identified by the upstream license and source files.

The packaged CPython binaries and standard library are supplied through the
Chaquopy target artifacts pinned in `locks/python-runtime.lock`. No third-party
Python packages or online `pip` installation are part of this release scope.
The complete upstream `v3.13.9` license and incorporated-software notices are
packaged as `third_party_licenses/CPython-3.13.9-LICENSE.txt`.

## AutoJs6 Python Runtime Plugin source

The plugin's own source code is licensed under the Mozilla Public License 2.0;
the complete text is in the repository root `LICENSE` file. The authorized
official source repository is:

https://github.com/SuperMonster003/AutoJs6-Plugin-Python-Runtime

The 0.1.0 release is still being prepared: `v0.1.0` has not yet been tagged or
published. Once published, source corresponding to a distributed build will be
available from its matching release tag or recorded commit in that repository.
If a binary was obtained from a mirror, use its version/build identity to select
the matching tag or commit. Release preparation must preserve this notice, the
root `LICENSE`, the exact source revision, and the dependency locks; this
document alone is not a substitute for the full license texts.
