"""Run as a Python file in AutoJs6 on an ARM64 device with 16 KiB pages.

This checks the Plugin process and selected native stdlib operations. The Host
APK needs its own ELF audit: successful Python execution does not establish
that the Host runs without Android's page-size compatibility mode.
"""

import bz2
import ctypes
import hashlib
import json
import lzma
import mmap
import os
import platform
import socket
import sqlite3
import ssl
import sys
import tempfile
import zlib

from autojs6 import artifacts, result


page_size = os.sysconf("SC_PAGE_SIZE")
libc = ctypes.CDLL(None)
libc.getpagesize.restype = ctypes.c_int
libc_page_size = libc.getpagesize()
assert platform.machine() == "aarch64", platform.machine()
assert page_size == 16384, page_size
assert libc_page_size == page_size, libc_page_size
assert mmap.PAGESIZE == page_size, mmap.PAGESIZE
assert mmap.ALLOCATIONGRANULARITY == page_size, mmap.ALLOCATIONGRANULARITY
assert sys.version_info[:3] == (3, 13, 9), sys.version

payload = bytes(range(256)) * 257 + "16 KiB / Python / 雪山".encode("utf-8")
for codec in (zlib, bz2, lzma):
    assert codec.decompress(codec.compress(payload)) == payload, codec.__name__

with mmap.mmap(-1, 2 * page_size) as mapping:
    mapping[page_size - 2:page_size + 2] = b"16KB"
    assert mapping[page_size - 2:page_size + 2] == b"16KB"
with tempfile.TemporaryFile() as backing:
    backing.write(b"\0" * page_size + b"M" * page_size)
    backing.flush()
    with mmap.mmap(backing.fileno(), page_size, offset=page_size) as mapping:
        assert mapping[:] == b"M" * page_size

callback = ctypes.CFUNCTYPE(ctypes.c_int, ctypes.c_int)(lambda value: value + 1)
assert callback(41) == 42
connection = sqlite3.connect(":memory:")
try:
    connection.execute("CREATE TABLE probe (value BLOB)")
    connection.execute("INSERT INTO probe VALUES (?)", (payload,))
    assert connection.execute("SELECT value FROM probe").fetchone()[0] == payload
finally:
    connection.close()
assert ssl.create_default_context().verify_mode == ssl.CERT_REQUIRED
sender, receiver = socket.socketpair()
try:
    sender.sendall(b"16KB")
    assert receiver.recv(4) == b"16KB"
finally:
    sender.close()
    receiver.close()

# Android can map native libraries directly from base.apk, so smaps need not
# expose a separate libpython filename. Check the process's mapping page sizes.
kernel_page_sizes_kib = set()
with open("/proc/self/smaps", encoding="utf-8") as smaps:
    for line in smaps:
        if line.startswith("KernelPageSize:"):
            kernel_page_sizes_kib.add(int(line.split()[1]))
assert kernel_page_sizes_kib == {16}, kernel_page_sizes_kib

report = {
    "schema": "autojs6-python-arm64-16k-probe-v1",
    "status": "PASS",
    "python": platform.python_version(),
    "machine": platform.machine(),
    "pluginPid": os.getpid(),
    "sysconfPageSize": page_size,
    "libcPageSize": libc_page_size,
    "mmapPageSize": mmap.PAGESIZE,
    "mmapAllocationGranularity": mmap.ALLOCATIONGRANULARITY,
    "kernelPageSizesKiB": sorted(kernel_page_sizes_kib),
    "checks": ["zlib", "bz2", "lzma", "anonymous-mmap", "file-mmap-offset",
               "ctypes-callback", "sqlite3", "ssl-context", "socketpair"],
    "payloadSha256": hashlib.sha256(payload).hexdigest(),
    "openssl": ssl.OPENSSL_VERSION,
    "sqlite": sqlite3.sqlite_version,
}
with open(artifacts.path("device/arm64-16k.json"), "w", encoding="utf-8") as output:
    json.dump(report, output, ensure_ascii=False, sort_keys=True)
    output.write("\n")
result.set(report)
print("ARM64-16K-PROBE-PASS " + json.dumps(report, sort_keys=True), flush=True)
