from __future__ import annotations

import sys

from autojs6 import result


print("M6-03-SNAPSHOT-BEGIN")
first = input("M6-03 snapshot prompt> ")
rest = sys.stdin.read()
after_eof = sys.stdin.readline()

if first != "快照值 αβ":
    raise AssertionError("stdin snapshot first line mismatch")
if rest != "剩余行 Ω\n":
    raise AssertionError("stdin snapshot remaining text mismatch")
if after_eof != "":
    raise AssertionError("stdin snapshot did not reach EOF")

print("M6-03-SNAPSHOT-PASS")
result.set(
    {
        "case": "M6-03A",
        "first": first,
        "rest": rest,
        "eof": after_eof == "",
    }
)
