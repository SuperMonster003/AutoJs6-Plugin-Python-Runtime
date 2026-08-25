from __future__ import annotations

import hashlib
from pathlib import Path

from autojs6 import artifacts, result


EXPECTED = b"\x00AUTOJS6-M6-04\xff\r\n\x01\x02\x03\x7f\x80\xfeBINARY-END\x00"
EXPECTED_SHA256 = "2B4A5E4BB7EB7C83D6241C5176D01EEDD31873FA63B28DE10F5553D8FBD25BD4"

print("M6-04-RESULT-ARTIFACT-BEGIN")
target = Path(artifacts.path("m6/expected.bin"))
written = target.write_bytes(EXPECTED)
digest = hashlib.sha256(target.read_bytes()).hexdigest().upper()

if written != 34 or len(EXPECTED) != 34:
    raise AssertionError("binary artifact length mismatch")
if digest != EXPECTED_SHA256:
    raise AssertionError("binary artifact digest mismatch")

print(f"M6-04-RESULT-ARTIFACT-PASS bytes={written} sha256={digest}")
result.set(
    {
        "case": "M6-04A",
        "ok": True,
        "artifact": "m6/expected.bin",
        "bytes": written,
        "sha256": digest,
        "hex": EXPECTED.hex(),
    }
)
