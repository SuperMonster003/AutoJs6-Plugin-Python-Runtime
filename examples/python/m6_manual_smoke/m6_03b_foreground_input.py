from __future__ import annotations

from getpass import getpass

from autojs6 import result


print("M6-03-FOREGROUND-BEGIN")
visible = input("Enter AUTOJS6-VISIBLE: ")
secret = getpass("Enter the hidden value from README: ")

if visible != "AUTOJS6-VISIBLE":
    raise AssertionError("visible input mismatch")
if secret != "M6-HIDDEN-7f3a":
    raise AssertionError("hidden getpass input mismatch")

print(f"M6-03-FOREGROUND-PASS visible_length={len(visible)} secret_length={len(secret)}")
result.set(
    {
        "case": "M6-03B",
        "inputMatched": True,
        "getpassMatched": True,
        "visibleLength": len(visible),
        "secretLength": len(secret),
    }
)
