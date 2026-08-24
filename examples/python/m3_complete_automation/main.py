"""Run one real, bounded Settings automation workflow.

The workflow launches Android Settings, finds and clicks its search control, verifies the
destination UI, captures a PNG artifact, and asserts that the verified destination control lies
inside the captured PNG. It changes no Settings value.
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
SETTINGS_SUBPAGE_RESOURCE_ID = "com.android.settings:id/content_parent"
OPEN_SEARCH_RESOURCE_ID = (
    "com.google.android.settings.intelligence:id/open_search_view_edit_text"
)
ARTIFACT_PATH = "screens/settings-search.png"

STARTUP_TIMEOUT_SECONDS = 10.0
DESTINATION_TIMEOUT_SECONDS = 8.0
POLL_INTERVAL_SECONDS = 0.25
MAX_BACK_STEPS = 4


def _find_exact(
    *,
    resource_id: str,
    package_name: str,
    class_name: str | None = None,
    clickable: bool | None = None,
) -> dict[str, object] | None:
    node = selector.find(
        resource_id=resource_id,
        class_name=class_name,
        clickable=clickable,
        enabled=True,
        max_nodes=512,
        max_depth=32,
    )
    if node is None:
        return None
    if node["resourceId"] != resource_id or node["packageName"] != package_name:
        raise RuntimeError(
            "Selector returned a resource match from an unexpected package: "
            f"resource={node['resourceId']!r}, package={node['packageName']!r}"
        )
    if node["enabled"] is not True:
        raise RuntimeError(f"Selector returned a disabled node for {resource_id}")
    # Android may expose the destination node before its enter animation makes it visible.
    # Treat that honest transient as "not ready yet" and let the bounded caller poll again.
    if node["visibleToUser"] is not True:
        return None
    return node


def _wait_for_home_search() -> tuple[dict[str, object], int]:
    deadline = time.monotonic() + STARTUP_TIMEOUT_SECONDS
    next_back_at = time.monotonic() + 1.0
    back_steps = 0
    last_surface = "unknown"

    while time.monotonic() < deadline:
        control = _find_exact(
            resource_id=HOME_SEARCH_RESOURCE_ID,
            package_name=SETTINGS_PACKAGE,
            clickable=True,
        )
        if control is not None:
            return control, back_steps

        # Android can resume an existing Settings subpage. Walk back only inside the known
        # Settings task, at a bounded rate, until its real homepage becomes visible.
        search_editor = _find_exact(
            resource_id=OPEN_SEARCH_RESOURCE_ID,
            package_name=SEARCH_PACKAGE,
            class_name="android.widget.EditText",
            clickable=True,
        )
        settings_content = None
        if search_editor is None:
            settings_content = _find_exact(
                resource_id=SETTINGS_SUBPAGE_RESOURCE_ID,
                package_name=SETTINGS_PACKAGE,
            )
        in_settings_task = search_editor is not None or settings_content is not None
        if search_editor is not None:
            last_surface = "Settings search"
        elif settings_content is not None:
            last_surface = "Settings subpage"
        else:
            last_surface = "outside Settings"
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
        f"last surface: {last_surface}"
    )


def _wait_for_search_destination() -> dict[str, object]:
    deadline = time.monotonic() + DESTINATION_TIMEOUT_SECONDS

    while time.monotonic() < deadline:
        editor = _find_exact(
            resource_id=OPEN_SEARCH_RESOURCE_ID,
            package_name=SEARCH_PACKAGE,
            class_name="android.widget.EditText",
            clickable=True,
        )
        if editor is not None:
            return editor
        time.sleep(POLL_INTERVAL_SECONDS)

    raise RuntimeError("Settings search destination did not appear before the bounded deadline")


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


def _assert_node_inside_png(
    node: dict[str, object],
    *,
    width: int,
    height: int,
) -> dict[str, int]:
    bounds = node["bounds"]
    left = bounds["left"]
    top = bounds["top"]
    right = bounds["right"]
    bottom = bounds["bottom"]
    if not (0 <= left < right <= width and 0 <= top < bottom <= height):
        raise AssertionError(
            "Verified destination control lies outside the captured screenshot: "
            f"PNG={width}x{height}, bounds=({left}, {top}, {right}, {bottom})"
        )
    return {"left": left, "top": top, "right": right, "bottom": bottom}


def run() -> dict[str, object]:
    print(f"Launching {SETTINGS_PACKAGE}")
    if not app.launch(SETTINGS_PACKAGE):
        raise RuntimeError("Android Settings could not be launched")

    search_control, back_steps = _wait_for_home_search()
    print(f"Found Settings search control: {search_control['resourceId']}")
    if not selector.click(search_control):
        raise RuntimeError("Android rejected the Settings search control click")

    editor = _wait_for_search_destination()
    print(f"Reached Settings search destination: {editor['resourceId']}")

    private_path = images.capture_screen(
        format="png",
        quality=100,
        path=ARTIFACT_PATH,
    )
    png_width, png_height, png_bytes = _assert_png(private_path)
    destination_bounds = _assert_node_inside_png(
        editor,
        width=png_width,
        height=png_height,
    )

    print(
        f"Screenshot assertion passed: {png_width}x{png_height}, "
        f"{png_bytes} bytes -> {ARTIFACT_PATH}"
    )
    return {
        "targetPackage": SETTINGS_PACKAGE,
        "destinationPackage": SEARCH_PACKAGE,
        "backSteps": back_steps,
        "controlResourceId": search_control["resourceId"],
        "destinationResourceId": editor["resourceId"],
        "destinationBounds": destination_bounds,
        "clicked": True,
        "screenshot": {
            "artifact": ARTIFACT_PATH,
            "format": "png",
            "width": png_width,
            "height": png_height,
            "bytes": png_bytes,
            "containsDestinationControl": True,
        },
    }


if __name__ == "__main__":
    result.set(run())
