"""Run one real, bounded Settings automation workflow.

The workflow launches Android Settings, finds and clicks its search control, verifies the
destination UI, captures a PNG artifact, and asserts that the PNG dimensions match the active UI
root. It changes no Settings value.
"""

from __future__ import annotations

import struct
import time
import zlib
from pathlib import Path

from autojs6 import app, automator, images, result, selector


SETTINGS_PACKAGE = "com.android.settings"
SEARCH_PACKAGE = "com.google.android.settings.intelligence"
HOME_SEARCH_RESOURCE_ID = "com.android.settings:id/search_action_bar"
OPEN_SEARCH_RESOURCE_ID = (
    "com.google.android.settings.intelligence:id/open_search_view_edit_text"
)
ARTIFACT_PATH = "screens/settings-search.png"

STARTUP_TIMEOUT_SECONDS = 10.0
DESTINATION_TIMEOUT_SECONDS = 8.0
POLL_INTERVAL_SECONDS = 0.25
MAX_BACK_STEPS = 4


def _find_node(
    tree: dict[str, object],
    *,
    resource_id: str,
    package_name: str,
) -> dict[str, object] | None:
    for node in tree["nodes"]:
        if (
            node["resourceId"] == resource_id
            and node["packageName"] == package_name
            and node["enabled"] is True
            and node["visibleToUser"] is True
        ):
            return node
    return None


def _packages(tree: dict[str, object]) -> tuple[str, ...]:
    return tuple(
        sorted(
            {
                node["packageName"]
                for node in tree["nodes"]
                if node["packageName"] is not None
            }
        )
    )


def _wait_for_home_search() -> tuple[dict[str, object], dict[str, object], int]:
    deadline = time.monotonic() + STARTUP_TIMEOUT_SECONDS
    next_back_at = time.monotonic() + 1.0
    back_steps = 0
    last_packages: tuple[str, ...] = ()

    while time.monotonic() < deadline:
        tree = selector.snapshot(max_nodes=128, max_depth=32)
        last_packages = _packages(tree)
        control = _find_node(
            tree,
            resource_id=HOME_SEARCH_RESOURCE_ID,
            package_name=SETTINGS_PACKAGE,
        )
        if control is not None and control["clickable"] is True:
            return tree, control, back_steps

        # Android can resume an existing Settings subpage. Walk back only inside the known
        # Settings task, at a bounded rate, until its real homepage becomes visible.
        in_settings_task = SETTINGS_PACKAGE in last_packages or SEARCH_PACKAGE in last_packages
        now = time.monotonic()
        if in_settings_task and back_steps < MAX_BACK_STEPS and now >= next_back_at:
            if not automator.back():
                raise RuntimeError("Android rejected Back while returning to the Settings home")
            back_steps += 1
            next_back_at = now + 0.5
            print(f"Returned one Settings level ({back_steps}/{MAX_BACK_STEPS})")

        time.sleep(POLL_INTERVAL_SECONDS)

    raise RuntimeError(
        "Settings search control did not appear before the bounded startup deadline; "
        f"last packages: {last_packages!r}"
    )


def _wait_for_search_destination() -> tuple[dict[str, object], dict[str, object]]:
    deadline = time.monotonic() + DESTINATION_TIMEOUT_SECONDS
    last_packages: tuple[str, ...] = ()

    while time.monotonic() < deadline:
        tree = selector.snapshot(max_nodes=128, max_depth=32)
        last_packages = _packages(tree)
        editor = _find_node(
            tree,
            resource_id=OPEN_SEARCH_RESOURCE_ID,
            package_name=SEARCH_PACKAGE,
        )
        if (
            editor is not None
            and editor["className"] == "android.widget.EditText"
            and editor["clickable"] is True
        ):
            return tree, editor
        time.sleep(POLL_INTERVAL_SECONDS)

    raise RuntimeError(
        "Settings search destination did not appear before the bounded deadline; "
        f"last packages: {last_packages!r}"
    )


def _assert_png(private_path: str) -> tuple[int, int, int]:
    path = Path(private_path)
    size = path.stat().st_size
    with path.open("rb") as stream:
        header = stream.read(33)

    if len(header) != 33 or header[:8] != b"\x89PNG\r\n\x1a\n":
        raise AssertionError("Captured artifact does not have a complete PNG header")
    if struct.unpack(">I", header[8:12])[0] != 13 or header[12:16] != b"IHDR":
        raise AssertionError("Captured artifact does not begin with a canonical PNG IHDR")

    expected_crc = struct.unpack(">I", header[29:33])[0]
    actual_crc = zlib.crc32(header[12:29]) & 0xFFFFFFFF
    if actual_crc != expected_crc:
        raise AssertionError("Captured PNG IHDR checksum is invalid")

    width, height = struct.unpack(">II", header[16:24])
    if width <= 0 or height <= 0:
        raise AssertionError("Captured PNG dimensions must be positive")
    return width, height, size


def _root_dimensions(tree: dict[str, object]) -> tuple[int, int]:
    root = tree["nodes"][0]
    bounds = root["bounds"]
    width = bounds["right"] - bounds["left"]
    height = bounds["bottom"] - bounds["top"]
    if width <= 0 or height <= 0:
        raise AssertionError("Active UI root has invalid bounds")
    return width, height


def run() -> dict[str, object]:
    print(f"Launching {SETTINGS_PACKAGE}")
    if not app.launch(SETTINGS_PACKAGE):
        raise RuntimeError("Android Settings could not be launched")

    home_tree, search_control, back_steps = _wait_for_home_search()
    print(f"Found Settings search control: {search_control['resourceId']}")
    if not selector.click(search_control):
        raise RuntimeError("Android rejected the Settings search control click")

    destination_tree, editor = _wait_for_search_destination()
    print(f"Reached Settings search destination: {editor['resourceId']}")

    private_path = images.capture_screen(
        format="png",
        quality=100,
        path=ARTIFACT_PATH,
    )
    png_width, png_height, png_bytes = _assert_png(private_path)
    ui_width, ui_height = _root_dimensions(destination_tree)
    if (png_width, png_height) != (ui_width, ui_height):
        raise AssertionError(
            "Screenshot dimensions do not match the verified destination UI: "
            f"PNG={png_width}x{png_height}, UI={ui_width}x{ui_height}"
        )

    print(
        f"Screenshot assertion passed: {png_width}x{png_height}, "
        f"{png_bytes} bytes -> {ARTIFACT_PATH}"
    )
    return {
        "targetPackage": SETTINGS_PACKAGE,
        "destinationPackage": SEARCH_PACKAGE,
        "homeNodes": len(home_tree["nodes"]),
        "backSteps": back_steps,
        "controlResourceId": search_control["resourceId"],
        "destinationResourceId": editor["resourceId"],
        "clicked": True,
        "screenshot": {
            "artifact": ARTIFACT_PATH,
            "format": "png",
            "width": png_width,
            "height": png_height,
            "bytes": png_bytes,
            "matchesUiBounds": True,
        },
    }


if __name__ == "__main__":
    result.set(run())
