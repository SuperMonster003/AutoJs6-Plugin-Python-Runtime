from __future__ import annotations

import json
import pathlib
import runpy
import struct
import sys
import tempfile
import types
import unittest
import zlib
from unittest import mock


ROOT = pathlib.Path(__file__).resolve().parents[2]
EXAMPLE = ROOT / "examples" / "python" / "m3_complete_automation"
MAIN = EXAMPLE / "main.py"

SETTINGS_PACKAGE = "com.android.settings"
SEARCH_PACKAGE = "com.google.android.settings.intelligence"
HOME_SEARCH_RESOURCE_ID = "com.android.settings:id/search_action_bar"
OPEN_SEARCH_RESOURCE_ID = (
    "com.google.android.settings.intelligence:id/open_search_view_edit_text"
)


def _node(
    node_id: str,
    *,
    package_name: str,
    resource_id: str | None = None,
    class_name: str = "android.widget.FrameLayout",
    clickable: bool = False,
    bounds: tuple[int, int, int, int] = (0, 0, 1080, 2424),
) -> dict[str, object]:
    left, top, right, bottom = bounds
    return {
        "id": node_id,
        "resourceId": resource_id,
        "packageName": package_name,
        "className": class_name,
        "clickable": clickable,
        "enabled": True,
        "visibleToUser": True,
        "bounds": {
            "left": left,
            "top": top,
            "right": right,
            "bottom": bottom,
        },
    }


def _tree(*nodes: dict[str, object]) -> dict[str, object]:
    return {"nodes": list(nodes)}


def _png_header(width: int, height: int) -> bytes:
    ihdr = struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0)
    checksum = zlib.crc32(b"IHDR" + ihdr) & 0xFFFFFFFF
    return (
        b"\x89PNG\r\n\x1a\n"
        + struct.pack(">I", len(ihdr))
        + b"IHDR"
        + ihdr
        + struct.pack(">I", checksum)
        + struct.pack(">I", 0)
        + b"IEND"
        + struct.pack(">I", zlib.crc32(b"IEND") & 0xFFFFFFFF)
    )


class _FakeSelector:
    def __init__(self) -> None:
        self.home_control = _node(
            "node-1-2",
            package_name=SETTINGS_PACKAGE,
            resource_id=HOME_SEARCH_RESOURCE_ID,
            class_name="android.widget.LinearLayout",
            clickable=True,
            bounds=(42, 163, 1038, 352),
        )
        self.destination_editor = _node(
            "node-2-2",
            package_name=SEARCH_PACKAGE,
            resource_id=OPEN_SEARCH_RESOURCE_ID,
            class_name="android.widget.EditText",
            clickable=True,
            bounds=(126, 142, 1080, 331),
        )
        self.snapshots = [
            _tree(
                _node("node-1-1", package_name=SETTINGS_PACKAGE),
                self.home_control,
            ),
            _tree(
                _node("node-2-1", package_name=SEARCH_PACKAGE),
                self.destination_editor,
            ),
        ]
        self.clicked: list[dict[str, object]] = []

    def snapshot(self, *, max_nodes: int, max_depth: int) -> dict[str, object]:
        if (max_nodes, max_depth) != (128, 32):
            raise AssertionError("Example changed its bounded selector profile")
        return self.snapshots.pop(0)

    def click(self, node: dict[str, object]) -> bool:
        self.clicked.append(node)
        return node is self.home_control


class M3CompleteAutomationExampleTest(unittest.TestCase):
    def test_project_is_a_bounded_public_python_project(self) -> None:
        self.assertEqual(
            {"README.md", "main.py", "project.json"},
            {path.name for path in EXAMPLE.iterdir()},
        )
        self.assertEqual(
            {"type": "python", "main": "main.py", "timeout": 60000},
            json.loads((EXAMPLE / "project.json").read_text(encoding="utf-8")),
        )

        source = MAIN.read_text(encoding="utf-8")
        compile(source, str(MAIN), "exec")
        for marker in (
            f'SETTINGS_PACKAGE = "{SETTINGS_PACKAGE}"',
            f'HOME_SEARCH_RESOURCE_ID = "{HOME_SEARCH_RESOURCE_ID}"',
            "MAX_BACK_STEPS = 4",
            "selector.click(search_control)",
            'images.capture_screen(',
            'path=ARTIFACT_PATH',
            'header[12:16] != b"IHDR"',
            '"matchesUiBounds": True',
            "result.set(run())",
        ):
            self.assertIn(marker, source)

        readme = (EXAMPLE / "README.md").read_text(encoding="utf-8")
        for marker in (
            "real Android Settings",
            "does not type a query or change any Settings value",
            "Android 11 or newer",
            "never enables it",
            "Vendor Settings applications",
            "screens/settings-search.png",
        ):
            self.assertIn(marker, readme)

    def test_workflow_sets_structured_result_after_screenshot_assertion(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            image = pathlib.Path(directory) / "settings-search.png"
            image.write_bytes(_png_header(1080, 2424))
            fake_selector = _FakeSelector()
            captured_results: list[dict[str, object]] = []
            capture_calls: list[dict[str, object]] = []

            def capture_screen(**arguments: object) -> str:
                capture_calls.append(arguments)
                return str(image)

            fake_autojs6 = types.ModuleType("autojs6")
            fake_autojs6.app = types.SimpleNamespace(
                launch=lambda package: package == SETTINGS_PACKAGE
            )
            fake_autojs6.automator = types.SimpleNamespace(
                back=lambda: self.fail("Back must not run when Settings opens at its homepage")
            )
            fake_autojs6.images = types.SimpleNamespace(capture_screen=capture_screen)
            fake_autojs6.result = types.SimpleNamespace(set=captured_results.append)
            fake_autojs6.selector = fake_selector

            with mock.patch.dict(sys.modules, {"autojs6": fake_autojs6}):
                runpy.run_path(str(MAIN), run_name="__main__")

        self.assertEqual([fake_selector.home_control], fake_selector.clicked)
        self.assertEqual(
            [{"format": "png", "quality": 100, "path": "screens/settings-search.png"}],
            capture_calls,
        )
        self.assertEqual(1, len(captured_results))
        outcome = captured_results[0]
        self.assertEqual(SETTINGS_PACKAGE, outcome["targetPackage"])
        self.assertEqual(SEARCH_PACKAGE, outcome["destinationPackage"])
        self.assertTrue(outcome["clicked"])
        self.assertEqual(0, outcome["backSteps"])
        self.assertEqual(
            {
                "artifact": "screens/settings-search.png",
                "format": "png",
                "width": 1080,
                "height": 2424,
                "bytes": 45,
                "matchesUiBounds": True,
            },
            outcome["screenshot"],
        )

    def test_mismatched_screenshot_and_ui_dimensions_fail_closed(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            image = pathlib.Path(directory) / "wrong-size.png"
            image.write_bytes(_png_header(720, 1280))
            fake_selector = _FakeSelector()
            captured_results: list[dict[str, object]] = []

            fake_autojs6 = types.ModuleType("autojs6")
            fake_autojs6.app = types.SimpleNamespace(launch=lambda _package: True)
            fake_autojs6.automator = types.SimpleNamespace(back=lambda: True)
            fake_autojs6.images = types.SimpleNamespace(
                capture_screen=lambda **_arguments: str(image)
            )
            fake_autojs6.result = types.SimpleNamespace(set=captured_results.append)
            fake_autojs6.selector = fake_selector

            with mock.patch.dict(sys.modules, {"autojs6": fake_autojs6}):
                with self.assertRaisesRegex(
                    AssertionError,
                    r"PNG=720x1280, UI=1080x2424",
                ):
                    runpy.run_path(str(MAIN), run_name="__main__")

        self.assertEqual([], captured_results)


if __name__ == "__main__":
    unittest.main()
