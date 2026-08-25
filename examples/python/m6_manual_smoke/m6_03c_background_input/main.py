from __future__ import annotations

import time

from autojs6 import result


print("M6-03-BACKGROUND-BEGIN")
started = time.monotonic()
try:
    input("M6-03 background input must not open a dialog> ")
except EOFError:
    elapsed_ms = round((time.monotonic() - started) * 1000)
else:
    raise AssertionError("background input unexpectedly returned a value")

if elapsed_ms > 5000:
    raise AssertionError("background input did not fail closed promptly")

print(f"M6-03-BACKGROUND-PASS error=EOFError elapsed_ms={elapsed_ms}")
result.set(
    {
        "case": "M6-03C",
        "failClosed": True,
        "error": "EOFError",
        "elapsedMillis": elapsed_ms,
    }
)
