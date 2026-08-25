from __future__ import annotations

import pathlib
import unittest
import xml.etree.ElementTree as ET


ROOT = pathlib.Path(__file__).resolve().parents[2]
MANIFEST = ROOT / "app" / "src" / "main" / "AndroidManifest.xml"
WAKE_ACTIVITY = (
    ROOT
    / "app"
    / "src"
    / "main"
    / "java"
    / "io"
    / "github"
    / "supermonster003"
    / "autojs6"
    / "plugin"
    / "python"
    / "runtime"
    / "WakeActivity.kt"
)
ANDROID = "{http://schemas.android.com/apk/res/android}"


class PluginActivationContractTest(unittest.TestCase):
    def setUp(self) -> None:
        self.application = ET.parse(MANIFEST).getroot().find("application")
        self.assertIsNotNone(self.application)

    def test_manifest_advertises_signature_protected_wake_activity(self) -> None:
        assert self.application is not None
        metadata = {
            item.get(ANDROID + "name"): item.get(ANDROID + "value")
            for item in self.application.findall("meta-data")
        }
        self.assertEqual(".WakeActivity", metadata.get("org.autojs.plugin.WAKE_ACTIVITY"))

        activity = next(
            (
                item
                for item in self.application.findall("activity")
                if item.get(ANDROID + "name") == ".WakeActivity"
            ),
            None,
        )
        self.assertIsNotNone(activity)
        assert activity is not None
        self.assertEqual("true", activity.get(ANDROID + "exported"))
        self.assertEqual("true", activity.get(ANDROID + "excludeFromRecents"))
        self.assertEqual("true", activity.get(ANDROID + "finishOnTaskLaunch"))
        self.assertEqual("org.autojs.permission.PLUGIN", activity.get(ANDROID + "permission"))
        self.assertEqual("@android:style/Theme.NoDisplay", activity.get(ANDROID + "theme"))

        actions = {
            item.get(ANDROID + "name")
            for item in activity.findall("intent-filter/action")
        }
        categories = {
            item.get(ANDROID + "name")
            for item in activity.findall("intent-filter/category")
        }
        self.assertEqual({"org.autojs.plugin.action.WAKE"}, actions)
        self.assertEqual({"android.intent.category.DEFAULT"}, categories)

    def test_wake_activity_finishes_without_initializing_python(self) -> None:
        source = WAKE_ACTIVITY.read_text(encoding="utf-8")
        self.assertIn("class WakeActivity : Activity()", source)
        self.assertIn("super.onCreate(savedInstanceState)", source)
        self.assertIn("finish()", source)
        self.assertNotIn("Python.start", source)
        self.assertNotIn("PythonRuntimePluginService", source)


if __name__ == "__main__":
    unittest.main()
