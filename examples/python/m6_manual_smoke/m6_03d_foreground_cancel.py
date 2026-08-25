from __future__ import annotations

from autojs6 import result


print("M6-03-CANCEL-BEGIN")
try:
    input("Press Cancel for M6-03D: ")
except KeyboardInterrupt:
    print("M6-03-CANCEL-PASS")
    result.set({"case": "M6-03D", "cancelled": True, "error": "KeyboardInterrupt"})
else:
    raise AssertionError("input returned; the Cancel button was not exercised")
