"""Capture one bounded PNG and publish it as an execution artifact.

Requires Android 11+ and an enabled, operational AutoJs6 accessibility service.
The API never enables accessibility or opens settings.
"""

from autojs6 import images, result


ARTIFACT_PATH = "screens/current.png"

private_path = images.capture_screen(
    format="png",
    quality=100,
    path=ARTIFACT_PATH,
)

result.set(
    {
        "artifact": ARTIFACT_PATH,
        "privatePath": private_path,
    }
)
