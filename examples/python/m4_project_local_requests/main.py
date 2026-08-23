"""Import a pure-Python dependency tree from this project and make HTTPS work."""

from importlib.metadata import version
from pathlib import Path

import certifi
import charset_normalizer
import idna
import requests
import urllib3
from autojs6 import result


project_root = Path(__file__).resolve().parent
requests_source = Path(requests.__file__).resolve()
if not requests_source.is_relative_to(project_root):
    raise RuntimeError(f"requests was not loaded from this project: {requests_source}")

response = requests.get("https://example.com/", timeout=15)
response.raise_for_status()

summary = {
    "status": response.status_code,
    "bytes": len(response.content),
    "requestsSource": requests_source.relative_to(project_root).as_posix(),
    "versions": {
        distribution: version(distribution)
        for distribution in (
            "requests",
            "urllib3",
            "certifi",
            "charset-normalizer",
            "idna",
        )
    },
}
print(
    f"HTTPS {summary['status']}; {summary['bytes']} bytes; "
    f"requests {summary['versions']['requests']} from {summary['requestsSource']}"
)
result.set(summary)
