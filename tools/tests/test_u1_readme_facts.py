from __future__ import annotations

import json
import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[2]
README_DIR = ROOT / ".readme"
LANGUAGE_CODES = (
    "zh-Hans",
    "zh-Hant-HK",
    "zh-Hant-TW",
    "en",
    "fr",
    "es",
    "ja",
    "ko",
    "ru",
    "ar",
)


class U1ReadmeFactsTest(unittest.TestCase):
    def test_all_language_sources_describe_current_protocol_and_existing_boundaries(self) -> None:
        common = json.loads((README_DIR / "common.json").read_text(encoding="utf-8"))
        self.assertEqual("0.5.0-alpha.4", common["release_target"])
        self.assertIn("protocol 1.5", common["release_state"])
        self.assertIn("protocol 1.6", common["release_state"])
        self.assertIn("foreground-only long-running", common["release_state"])
        self.assertIn("15-second Provider heartbeats", common["release_state"])
        self.assertIn("concurrent Python launches", common["release_state"])
        self.assertIn("fair FIFO", common["release_state"])
        self.assertIn("32 bounded waiters", common["release_state"])
        self.assertIn("3 seconds", common["release_state"])
        self.assertIn("single-session", common["release_state"])
        self.assertIn("no provider queue", common["release_state"])
        for marker in (
            "QV710AF65F",
            "Host versionCode 5276",
            "Plugin versionCode 81",
            "tick=70",
            "focused long-running Android smoke passes",
            "BUSY/SESSION_OPEN",
            "afca7b14c",
            "fresh-PID generation handoff",
            "queued Stop isolation",
            "focused concurrency Android smoke passes",
            "no-runtime-change startup probe",
            "441/447/429/427/428 ms",
            "five distinct Plugin PIDs",
            "all-sample median is 429 ms",
            "median excluding the first run is 428.5 ms",
            "maximum is 447 ms",
            "below the 1000 ms threshold",
            "process retention is not justified",
            "per-execution retirement remains",
            "M6 consolidates the unpublished 0.2/0.3/0.4",
            "cumulative 0.5.0 release train",
            "read-only source profile",
            "full local candidate gate",
            "ten-item manual Android smoke checklist",
            "neither profile uses ADB, signing, network, tagging, pushing, or publication",
            "exact signed-candidate smoke",
            "beta/stable promotion",
        ):
            self.assertIn(marker, common["release_state"])
        self.assertIn("bounded automator", common["release_state"])
        self.assertIn("selector/UI-tree", common["release_state"])
        self.assertIn("screen capture", common["release_state"])
        self.assertIn("find_color", common["release_state"])
        self.assertIn("find_image", common["release_state"])
        self.assertIn("Host OCR", common["release_state"])
        self.assertIn("complete Settings", common["release_state"])
        self.assertIn("M4 Path A", common["release_state"])
        self.assertIn("project-local pure-Python", common["release_state"])
        self.assertIn("M4 Path B", common["release_state"])
        self.assertIn("M4 Path C", common["release_state"])
        self.assertIn("NOT_ADMITTED", common["release_state"])
        self.assertIn("stdlib-only", common["release_state"])
        self.assertIn("zero packages", common["release_state"])
        self.assertIn("Pillow 11.0.0", common["release_state"])
        self.assertIn("NumPy 1.26.2", common["release_state"])
        self.assertIn("OpenCV", common["release_state"])
        self.assertIn("16 KiB gate", common["release_state"])
        self.assertIn("no candidate dependency payload", common["release_state"])
        self.assertIn("publication, and release evidence remain outside", common["release_state"])
        self.assertEqual("1 MiB", common["max_stdin_bytes"])
        self.assertEqual("64 MiB", common["max_workspace_archive_bytes"])
        self.assertEqual("8192", common["max_workspace_entries"])
        self.assertEqual("128 MiB", common["max_workspace_uncompressed_bytes"])
        self.assertEqual("1.0-1.6", common["protocol_version"])
        self.assertEqual("64 KiB", common["max_structured_json_bytes"])
        self.assertEqual("16", common["max_output_artifacts"])
        self.assertEqual("16 MiB", common["max_output_bytes"])
        self.assertEqual("16384", common["max_output_chunks"])
        self.assertEqual("30 min", common["max_timeout"])
        self.assertEqual("15 s", common["long_running_heartbeat_interval"])
        self.assertEqual("45 s", common["long_running_heartbeat_lease"])
        self.assertEqual("2 min", common["long_running_start_lease"])
        self.assertEqual("32", common["max_host_python_pending_executions"])
        self.assertEqual("3 s", common["python_process_retirement_wait"])
        self.assertEqual("1024", common["max_host_capability_calls"])
        self.assertEqual("64 KiB", common["max_host_capability_message_bytes"])
        self.assertEqual("32 KiB", common["max_host_capability_text_bytes"])
        self.assertEqual("5 s", common["host_capability_call_timeout"])
        self.assertEqual("4 KiB", common["max_host_file_path_bytes"])
        self.assertEqual("32 KiB", common["max_host_file_text_bytes"])
        self.assertEqual("128", common["max_host_file_entries"])
        self.assertEqual("255 UTF-8 bytes", common["max_host_file_name_bytes"])
        self.assertEqual("256 UTF-8 bytes", common["max_host_dialog_title_bytes"])
        self.assertEqual("4 KiB", common["max_host_dialog_text_bytes"])
        self.assertEqual("32 KiB", common["max_host_dialog_prompt_reply_bytes"])
        self.assertEqual("64", common["max_host_dialog_items"])
        self.assertEqual("1 KiB", common["max_host_dialog_item_bytes"])
        self.assertEqual("32 KiB", common["max_host_dialog_total_item_bytes"])
        self.assertEqual("5 min", common["host_dialog_wait_timeout"])
        self.assertEqual("16", common["max_host_engine_launches"])
        self.assertEqual("1000000", common["max_host_automator_coordinate"])
        self.assertEqual("4 s", common["max_host_automator_duration"])
        self.assertEqual("128", common["max_host_selector_snapshot_nodes"])
        self.assertEqual("1024", common["max_host_selector_find_nodes"])
        self.assertEqual("32", common["max_host_selector_depth"])
        self.assertEqual("48 KiB", common["max_host_selector_snapshot_value_bytes"])
        self.assertEqual("256 Unicode code points", common["max_host_selector_node_text"])
        self.assertEqual("1024 UTF-8 bytes", common["max_host_selector_query_text_bytes"])
        self.assertEqual("4 KiB", common["max_host_selector_set_text_bytes"])
        self.assertEqual("128", common["max_host_selector_retained_nodes"])
        self.assertEqual("1", common["max_host_screen_images"])
        self.assertEqual("4 MiB", common["max_host_screen_image_bytes"])
        self.assertEqual("32 KiB", common["max_host_screen_chunk_bytes"])
        self.assertEqual("8192", common["max_host_screen_dimension"])
        self.assertEqual("16777216", common["max_host_screen_pixels"])
        self.assertEqual("255", common["max_host_screen_color_threshold"])
        self.assertEqual("1", common["max_host_image_templates"])
        self.assertEqual("1 MiB", common["max_host_image_template_bytes"])
        self.assertEqual("24 KiB", common["max_host_image_template_chunk_bytes"])
        self.assertEqual("2048", common["max_host_image_template_dimension"])
        self.assertEqual("1048576", common["max_host_image_template_pixels"])
        self.assertEqual("4194304", common["max_host_image_match_region_pixels"])
        self.assertEqual("16777216", common["max_host_image_match_comparisons"])
        self.assertEqual("256", common["max_host_ocr_lines"])
        self.assertEqual("4 KiB", common["max_host_ocr_line_bytes"])
        self.assertEqual("48 KiB", common["max_host_ocr_total_bytes"])
        self.assertEqual("60 s", common["host_ocr_call_timeout"])
        for code in LANGUAGE_CODES:
            with self.subTest(code=code):
                source = json.loads(
                    (README_DIR / f"lang_{code}.json").read_text(encoding="utf-8")
                )
                self.assertIn("{{ max_stdin_bytes }}", source["features"][1])
                self.assertIn("1.3", source["features"][1])
                self.assertIn("`getpass.getpass()`", source["features"][1])
                package_features = [item for item in source["features"] if ".dist-info" in item]
                self.assertEqual(1, len(package_features))
                self.assertIn("pip", package_features[0])
                result_features = [item for item in source["features"] if "1.4" in item]
                self.assertEqual(1, len(result_features))
                self.assertIn("{{ max_structured_json_bytes }}", result_features[0])
                self.assertIn("{{ max_output_artifacts }}", result_features[0])
                self.assertIn("stdout", result_features[0])
                broker_features = [item for item in source["features"] if "1.5" in item]
                self.assertEqual(1, len(broker_features))
                self.assertIn("`toast`", broker_features[0])
                self.assertIn("`clip.get/set`", broker_features[0])
                self.assertIn("`app.launch/launch_app/open_url`", broker_features[0])
                self.assertIn("`device.info`", broker_features[0])
                self.assertIn("`console.log/warn/error`", broker_features[0])
                self.assertIn("`notice`", broker_features[0])
                self.assertIn(
                    "`files.read_text/write_text/exists/is_file/is_dir/list`",
                    broker_features[0],
                )
                self.assertIn("`dialogs.alert/confirm/prompt/select`", broker_features[0])
                self.assertIn("`engines.current/run/stop_self`", broker_features[0])
                self.assertIn(
                    "`automator.click/long_click/press/swipe/back/home`",
                    broker_features[0],
                )
                self.assertIn(
                    "`selector.snapshot/find/click/set_text`",
                    broker_features[0],
                )
                self.assertIn("`images.capture_screen`", broker_features[0])
                self.assertIn("`images.find_color`", broker_features[0])
                self.assertIn("`images.find_image`", broker_features[0])
                self.assertIn("`ocr.recognize`", broker_features[0])
                long_running_features = [
                    item for item in source["features"] if "1.6" in item
                ]
                self.assertEqual(1, len(long_running_features))
                self.assertIn("`executionMode=long-running`", long_running_features[0])
                self.assertIn(
                    "{{ long_running_heartbeat_interval }}", long_running_features[0]
                )
                self.assertIn("Stop", long_running_features[0])
                concurrency_features = [
                    item
                    for item in source["features"]
                    if "{{ max_host_python_pending_executions }}" in item
                ]
                self.assertEqual(1, len(concurrency_features))
                self.assertIn("FIFO", concurrency_features[0])
                self.assertIn(
                    "{{ python_process_retirement_wait }}", concurrency_features[0]
                )
                self.assertIn("Provider", concurrency_features[0])
                self.assertIn("{{ max_stdin_bytes }}", source["p_plugin_scope"])
                self.assertIn("1.3", source["p_plugin_scope"])
                self.assertIn("1.4", source["p_plugin_scope"])
                self.assertIn("1.5", source["p_plugin_scope"])
                self.assertIn("SHA-256", source["p_plugin_scope"])
                self.assertIn("stdout", source["p_plugin_scope"])
                self.assertIn("`sys.stdin`", source["p_plugin_scope"])
                self.assertIn("`getpass.getpass()`", source["p_plugin_scope"])
                self.assertIn("`INTERACTIVE_NOT_ALLOWED`", source["p_plugin_scope"])
                result_limits = [
                    item
                    for item in source["security_limits"]
                    if "{{ max_structured_json_bytes }}" in item
                ]
                self.assertEqual(1, len(result_limits))
                for placeholder in (
                    "{{ max_structured_json_bytes }}",
                    "{{ max_output_artifacts }}",
                    "{{ max_output_artifact_path_bytes }}",
                    "{{ max_output_artifact_bytes }}",
                    "{{ max_total_output_artifact_bytes }}",
                ):
                    self.assertIn(placeholder, result_limits[0])
                broker_limits = [item for item in source["security_limits"] if "1.5" in item]
                self.assertEqual(1, len(broker_limits))
                for placeholder in (
                    "{{ max_host_capability_calls }}",
                    "{{ max_host_capability_message_bytes }}",
                    "{{ max_host_capability_text_bytes }}",
                    "{{ host_capability_call_timeout }}",
                    "{{ max_host_file_path_bytes }}",
                    "{{ max_host_file_text_bytes }}",
                    "{{ max_host_file_entries }}",
                    "{{ max_host_file_name_bytes }}",
                    "{{ max_host_dialog_title_bytes }}",
                    "{{ max_host_dialog_text_bytes }}",
                    "{{ max_host_dialog_prompt_reply_bytes }}",
                    "{{ max_host_dialog_items }}",
                    "{{ max_host_dialog_item_bytes }}",
                    "{{ max_host_dialog_total_item_bytes }}",
                    "{{ host_dialog_wait_timeout }}",
                    "{{ max_host_engine_launches }}",
                ):
                    self.assertIn(placeholder, broker_limits[0])
                long_running_limits = [
                    item
                    for item in source["security_limits"]
                    if "{{ long_running_heartbeat_lease }}" in item
                ]
                self.assertEqual(1, len(long_running_limits))
                for placeholder in (
                    "{{ max_timeout }}",
                    "{{ long_running_start_lease }}",
                    "{{ long_running_heartbeat_lease }}",
                ):
                    self.assertIn(placeholder, long_running_limits[0])
                automator_limits = [
                    item
                    for item in source["security_limits"]
                    if "{{ max_host_automator_coordinate }}" in item
                ]
                self.assertEqual(1, len(automator_limits))
                self.assertIn("{{ max_host_automator_duration }}", automator_limits[0])
                self.assertIn("`CapabilityUnavailableError`", automator_limits[0])
                selector_limits = [
                    item
                    for item in source["security_limits"]
                    if "{{ max_host_selector_snapshot_nodes }}" in item
                ]
                self.assertEqual(1, len(selector_limits))
                for placeholder in (
                    "{{ max_host_selector_snapshot_nodes }}",
                    "{{ max_host_selector_find_nodes }}",
                    "{{ max_host_selector_depth }}",
                    "{{ max_host_selector_snapshot_value_bytes }}",
                    "{{ max_host_selector_node_text }}",
                    "{{ max_host_selector_query_text_bytes }}",
                    "{{ max_host_selector_set_text_bytes }}",
                    "{{ max_host_selector_retained_nodes }}",
                ):
                    self.assertIn(placeholder, selector_limits[0])
                self.assertIn("`SELECTOR_SCAN_LIMIT_EXCEEDED`", selector_limits[0])
                self.assertIn("`STALE_NODE`", selector_limits[0])
                image_limits = [
                    item
                    for item in source["security_limits"]
                    if "{{ max_host_screen_images }}" in item
                ]
                self.assertEqual(1, len(image_limits))
                for placeholder in (
                    "{{ max_host_screen_images }}",
                    "{{ max_host_screen_image_bytes }}",
                    "{{ max_host_screen_chunk_bytes }}",
                    "{{ max_host_screen_dimension }}",
                    "{{ max_host_screen_pixels }}",
                    "{{ max_host_screen_color_threshold }}",
                    "{{ max_host_image_templates }}",
                    "{{ max_host_image_template_bytes }}",
                    "{{ max_host_image_template_chunk_bytes }}",
                    "{{ max_host_image_template_dimension }}",
                    "{{ max_host_image_template_pixels }}",
                    "{{ max_host_image_match_region_pixels }}",
                    "{{ max_host_image_match_comparisons }}",
                ):
                    self.assertIn(placeholder, image_limits[0])
                for error_code in (
                    "`CapabilityUnavailableError`",
                    "`SCREEN_CAPTURE_FAILED`",
                    "`RESULT_LIMIT_EXCEEDED`",
                    "`STALE_IMAGE`",
                ):
                    self.assertIn(error_code, image_limits[0])
                ocr_limits = [
                    item
                    for item in source["security_limits"]
                    if "{{ max_host_ocr_lines }}" in item
                ]
                self.assertEqual(1, len(ocr_limits))
                for placeholder in (
                    "{{ max_host_image_template_bytes }}",
                    "{{ max_host_image_template_chunk_bytes }}",
                    "{{ max_host_image_template_dimension }}",
                    "{{ max_host_image_template_pixels }}",
                    "{{ max_host_ocr_lines }}",
                    "{{ max_host_ocr_line_bytes }}",
                    "{{ max_host_ocr_total_bytes }}",
                    "{{ host_ocr_call_timeout }}",
                ):
                    self.assertIn(placeholder, ocr_limits[0])
                self.assertIn("`OCR_UNAVAILABLE`", ocr_limits[0])
                self.assertIn("`OCR_FAILED`", ocr_limits[0])
                network_limits = [item for item in source["security_limits"] if "INTERNET" in item]
                self.assertEqual(1, len(network_limits))
                self.assertIn("pip", network_limits[0])
                workspace_limits = [
                    item
                    for item in source["security_limits"]
                    if "{{ max_workspace_archive_bytes }}" in item
                ]
                self.assertEqual(1, len(workspace_limits))
                for placeholder in (
                    "{{ max_workspace_archive_bytes }}",
                    "{{ max_workspace_entries }}",
                    "{{ max_workspace_uncompressed_bytes }}",
                ):
                    self.assertIn(placeholder, workspace_limits[0])
                self.assertIn("{{ max_stdin_bytes }}", source["unsupported_capabilities"][0])
                self.assertIn("`sys.stdin`", source["unsupported_capabilities"][0])
                self.assertIn("`getpass.getpass()`", source["unsupported_capabilities"][0])
                self.assertTrue(
                    any("OCR" in item for item in source["unsupported_capabilities"]),
                    f"{code} does not bound the remaining broker surface",
                )
                self.assertTrue(
                    any("selector" in item for item in source["unsupported_capabilities"]),
                    f"{code} does not describe the bounded selector/UI-tree surface",
                )
                self.assertTrue(
                    any("engines" in item for item in source["unsupported_capabilities"]),
                    f"{code} does not describe the bounded engines surface",
                )
                self.assertIn("16 KB", source["p_build_architecture"])
                self.assertIn("gate", source["p_build_architecture"].lower())
                self.assertIn("M4", source["p_roadmap"])
                for decision_marker in (
                    "M4",
                    "`NOT_ADMITTED`",
                    "`stdlib-only`",
                    "Path C",
                    "Pillow",
                    "NumPy",
                    "OpenCV",
                    "16 KiB",
                ):
                    self.assertIn(decision_marker, source["p_roadmap"])

    def test_all_changelog_sources_record_current_scoped_features(self) -> None:
        changelog_dir = ROOT / ".changelog"
        for code in LANGUAGE_CODES:
            with self.subTest(code=code):
                source = json.loads(
                    (changelog_dir / f"lang_{code}.json").read_text(encoding="utf-8")
                )
                long_running = source["$data"]["v0.5.0-alpha.1"]
                self.assertEqual("2026/08/24", long_running["released_date"])
                self.assertEqual(1, len(long_running["hint"]))
                self.assertEqual(1, len(long_running["feature"]))
                self.assertEqual(1, len(long_running["improvement"]))
                for marker in ("M5", "1.6", "Host/Plugin"):
                    self.assertIn(marker, long_running["hint"][0])
                for marker in (
                    "`executionMode=long-running`",
                    "`specialUse`",
                    "Stop",
                ):
                    self.assertIn(marker, long_running["feature"][0])
                for marker in ("15 s", "2 min", "45 s", "1.0-1.5"):
                    self.assertIn(marker, long_running["improvement"][0])

                concurrency = source["$data"]["v0.5.0-alpha.2"]
                self.assertEqual("2026/08/24", concurrency["released_date"])
                self.assertEqual(1, len(concurrency["hint"]))
                self.assertEqual(1, len(concurrency["feature"]))
                self.assertEqual(1, len(concurrency["improvement"]))
                self.assertIn("M5", concurrency["hint"][0])
                for marker in ("Host", "FIFO", "32"):
                    self.assertIn(marker, concurrency["feature"][0])
                for marker in ("3", "1.6", "AAR", "Plugin"):
                    self.assertIn(marker, concurrency["improvement"][0])

                cadence = source["$data"]["v0.5.0-alpha.4"]
                self.assertEqual("2026/08/25", cadence["released_date"])
                self.assertEqual(1, len(cadence["hint"]))
                self.assertEqual(1, len(cadence["feature"]))
                self.assertEqual(1, len(cadence["improvement"]))
                self.assertNotIn("fix", cadence)
                self.assertNotIn("dependency", cadence)
                for marker in ("M6", "0.2/0.3/0.4", "0.5.0"):
                    self.assertIn(marker, cadence["hint"][0])
                for marker in (
                    "`tools/verify-m6-candidate.py`",
                    "`--source-only`",
                    "`--full`",
                    "R2",
                    "offline",
                ):
                    self.assertIn(marker, cadence["feature"][0])
                for marker in (
                    "10",
                    "alpha",
                    "beta",
                    "0.5.0",
                    "ADB",
                    "signing",
                    "publication",
                ):
                    self.assertIn(marker, cadence["improvement"][0])

                prewarm = source["$data"]["v0.5.0-alpha.3"]
                self.assertEqual("2026/08/24", prewarm["released_date"])
                self.assertEqual(1, len(prewarm["hint"]))
                self.assertNotIn("feature", prewarm)
                self.assertNotIn("fix", prewarm)
                self.assertNotIn("dependency", prewarm)
                self.assertEqual(2, len(prewarm["improvement"]))
                for marker in ("M5", "QV710AF65F"):
                    self.assertIn(marker, prewarm["hint"][0])
                for marker in (
                    "441/447/429/427/428 ms",
                    "429 ms",
                    "428.5 ms",
                    "447 ms",
                    "Plugin",
                ):
                    self.assertIn(marker, prewarm["improvement"][0])
                for marker in ("1000 ms", "per-execution", "keep-process"):
                    self.assertIn(marker, prewarm["improvement"][1])

                native_policy = source["$data"]["v0.4.0-alpha.9"]
                self.assertEqual("2026/08/24", native_policy["released_date"])
                self.assertNotIn("feature", native_policy)
                self.assertNotIn("fix", native_policy)
                self.assertNotIn("dependency", native_policy)
                self.assertEqual(1, len(native_policy["hint"]))
                for marker in (
                    "M4 Path C",
                    "`NOT_ADMITTED`",
                    "`stdlib-only`",
                    "Pillow",
                    "NumPy",
                    "OpenCV",
                ):
                    self.assertIn(marker, native_policy["hint"][0])
                self.assertEqual(2, len(native_policy["improvement"]))
                for marker in (
                    "ADR 0004",
                    "`--no-index --find-links`",
                    "Pillow 11.0.0",
                    "2,054,483",
                    "NumPy 1.26.2",
                    "21,931,164",
                    "`zipalign -c -P 16 4`",
                ):
                    self.assertIn(marker, native_policy["improvement"][0])
                for marker in (
                    "NDK 29",
                    "FreeType",
                    "`0x1000`",
                    "OpenBLAS/libgfortran",
                    "OpenCV",
                    "`cp313`",
                    "NDK r28+",
                    "16 KiB",
                ):
                    self.assertIn(marker, native_policy["improvement"][1])

                package_policy = source["$data"]["v0.4.0-alpha.8"]
                self.assertEqual("2026/08/24", package_policy["released_date"])
                self.assertNotIn("feature", package_policy)
                self.assertEqual(1, len(package_policy["hint"]))
                for marker in (
                    "M4 Path B",
                    "`NOT_ADMITTED`",
                    "`stdlib-only`",
                    "`requests`",
                ):
                    self.assertIn(marker, package_policy["hint"][0])
                self.assertEqual(1, len(package_policy["improvement"]))
                for marker in (
                    "debug APK",
                    "23,709,688",
                    "23,726,048",
                    "34,622,039",
                    "Gradle `--offline`",
                    "`--no-index`",
                    "`--require-hashes`",
                    "dual ABI",
                ):
                    self.assertIn(marker, package_policy["improvement"][0])

                complete_automation = source["$data"]["v0.4.0-alpha.7"]
                self.assertEqual("2026/08/24", complete_automation["released_date"])
                self.assertEqual(1, len(complete_automation["feature"]))
                for method in (
                    "m3_complete_automation",
                    "app.launch",
                    "selector.find",
                    "selector.click",
                    "images.capture_screen",
                ):
                    self.assertIn(method, complete_automation["feature"][0])
                self.assertEqual(1, len(complete_automation["fix"]))
                for boundary in ("right < left", "bottom < top", "zero-area"):
                    self.assertIn(boundary, complete_automation["fix"][0])
                self.assertEqual(1, len(complete_automation["improvement"]))
                for evidence in (
                    "RunIntentActivity",
                    "API 37",
                    "1080x2424",
                    "SHA-256",
                    "0/null",
                ):
                    self.assertIn(evidence, complete_automation["improvement"][0])

                host_ocr = source["$data"]["v0.4.0-alpha.6"]
                self.assertEqual("2026/08/24", host_ocr["released_date"])
                self.assertEqual(1, len(host_ocr["feature"]))
                self.assertIn("ocr.recognize", host_ocr["feature"][0])
                self.assertIn("PNG/JPEG", host_ocr["feature"][0])
                for boundary in (
                    "1 MiB",
                    "24 KiB",
                    "SHA-256",
                    "256",
                    "4 KiB",
                    "48 KiB",
                    "OCR_UNAVAILABLE",
                    "OCR_FAILED",
                    "release",
                ):
                    self.assertIn(boundary, host_ocr["improvement"][0])

                template_image = source["$data"]["v0.4.0-alpha.5"]
                self.assertEqual("2026/08/24", template_image["released_date"])
                self.assertEqual(1, len(template_image["feature"]))
                self.assertIn("find_image", template_image["feature"][0])
                self.assertIn("PNG/JPEG", template_image["feature"][0])
                for boundary in (
                    "1 MiB",
                    "24 KiB",
                    "SHA-256",
                    "2048",
                    "row-major",
                    "autojs6-python-image-match-v1",
                    "OpenCV",
                    "release",
                    "333 ms",
                    "350 ms",
                ):
                    self.assertIn(boundary, template_image["improvement"][0])

                screen_color = source["$data"]["v0.4.0-alpha.4"]
                self.assertEqual("2026/08/24", screen_color["released_date"])
                self.assertEqual(1, len(screen_color["feature"]))
                self.assertIn("find_color", screen_color["feature"][0])
                self.assertIn("#RRGGBB", screen_color["feature"][0])
                for boundary in (
                    "255",
                    "row-major",
                    "autojs6-python-color-match-v1",
                    "Python",
                ):
                    self.assertIn(boundary, screen_color["improvement"][0])

                screen_capture = source["$data"]["v0.4.0-alpha.3"]
                self.assertEqual("2026/08/24", screen_capture["released_date"])
                self.assertEqual(1, len(screen_capture["feature"]))
                self.assertIn("capture_screen", screen_capture["feature"][0])
                self.assertIn("PNG/JPEG", screen_capture["feature"][0])
                for boundary in ("1", "32 KiB", "4 MiB", "SHA-256", "release"):
                    self.assertIn(boundary, screen_capture["improvement"][0])

                selector = source["$data"]["v0.4.0-alpha.2"]
                self.assertEqual("2026/08/24", selector["released_date"])
                self.assertEqual(1, len(selector["feature"]))
                for method in ("snapshot", "find", "click", "set_text"):
                    self.assertIn(method, selector["feature"][0])
                self.assertIn("`SELECTOR_SCAN_LIMIT_EXCEEDED`", selector["improvement"][0])
                self.assertIn("`STALE_NODE`", selector["improvement"][0])
                self.assertIn("`CapabilityUnavailableError`", selector["improvement"][0])

                automator = source["$data"]["v0.4.0-alpha.1"]
                self.assertEqual("2026/08/23", automator["released_date"])
                self.assertEqual(1, len(automator["feature"]))
                for method in ("click", "long_click", "press", "swipe", "back", "home"):
                    self.assertIn(method, automator["feature"][0])
                self.assertIn("1000000", automator["improvement"][0])
                self.assertIn("4000", automator["improvement"][0])
                self.assertIn("`CapabilityUnavailableError`", automator["improvement"][0])

                project_packages = source["$data"]["v0.3.0-alpha.6"]
                self.assertEqual("2026/08/23", project_packages["released_date"])
                self.assertEqual(1, len(project_packages["feature"]))
                self.assertIn("`.dist-info`", project_packages["feature"][0])
                self.assertIn("`requests`", project_packages["feature"][0])
                self.assertIn("64 MiB", project_packages["improvement"][0])
                self.assertIn("8192", project_packages["improvement"][0])
                self.assertIn("128 MiB", project_packages["improvement"][0])
                self.assertIn("`ModuleNotFoundError`", project_packages["improvement"][0])

                host_engines = source["$data"]["v0.3.0-alpha.5"]
                self.assertEqual("2026/08/23", host_engines["released_date"])
                self.assertEqual(1, len(host_engines["feature"]))
                for method in ("current", "run", "stop_self"):
                    self.assertIn(method, host_engines["feature"][0])
                self.assertIn("16", host_engines["improvement"][0])
                self.assertIn(
                    "`NESTED_PYTHON_NOT_ALLOWED`",
                    host_engines["improvement"][0],
                )

                host_dialogs = source["$data"]["v0.3.0-alpha.4"]
                self.assertEqual("2026/08/23", host_dialogs["released_date"])
                self.assertEqual(1, len(host_dialogs["feature"]))
                for method in ("alert", "confirm", "prompt", "select"):
                    self.assertIn(method, host_dialogs["feature"][0])
                self.assertIn(
                    "`INTERACTIVE_NOT_ALLOWED`",
                    host_dialogs["improvement"][0],
                )
                self.assertIn("Host", host_dialogs["improvement"][0])

                host_files = source["$data"]["v0.3.0-alpha.3"]
                self.assertEqual("2026/08/23", host_files["released_date"])
                self.assertEqual(1, len(host_files["feature"]))
                for method in (
                    "read_text",
                    "write_text",
                    "exists",
                    "is_file",
                    "is_dir",
                    "list",
                ):
                    self.assertIn(method, host_files["feature"][0])
                self.assertIn("Host", host_files["improvement"][0])
                self.assertIn("workspace", host_files["improvement"][0])

                complete_slice = source["$data"]["v0.3.0-alpha.2"]
                self.assertEqual("2026/08/23", complete_slice["released_date"])
                public_api = complete_slice["feature"]
                self.assertEqual(1, len(public_api))
                self.assertIn("`autojs6.device.info()`", public_api[0])
                self.assertIn("`autojs6.console.log/warn/error`", public_api[0])
                self.assertIn("`autojs6.notice`", public_api[0])
                self.assertIn("`PERMISSION_DENIED`", complete_slice["improvement"][0])

                broker = source["$data"]["v0.3.0-alpha.1"]
                self.assertEqual("2026/08/23", broker["released_date"])
                protocol_15 = [item for item in broker["feature"] if "1.5" in item]
                self.assertEqual(1, len(protocol_15))
                self.assertIn("1024", protocol_15[0])
                self.assertIn("64 KiB", protocol_15[0])
                public_api = [item for item in broker["feature"] if "`autojs6.toast`" in item]
                self.assertEqual(1, len(public_api))
                self.assertIn("`autojs6.clip.get/set`", public_api[0])
                self.assertIn("`autojs6.app.launch/launch_app/open_url`", public_api[0])
                current = source["$data"]["v0.2.0-alpha.1"]
                self.assertIn("E2", current["hint"][0])
                self.assertIn("R2 E3", current["hint"][0])
                protocol_13 = [item for item in current["feature"] if "1.3" in item]
                protocol_14 = [item for item in current["feature"] if "1.4" in item]
                self.assertEqual(1, len(protocol_13))
                self.assertEqual(1, len(protocol_14))
                self.assertIn("`input()`", protocol_13[0])
                self.assertIn("`getpass.getpass()`", protocol_13[0])
                self.assertIn("`sys.stdin`", protocol_13[0])
                self.assertIn("SHA-256", protocol_14[0])
                self.assertIn("stdout", protocol_14[0])
                network_changes = [item for item in current["improvement"] if "INTERNET" in item]
                limit_changes = [item for item in current["improvement"] if "16 MiB" in item]
                self.assertEqual(1, len(network_changes))
                self.assertEqual(1, len(limit_changes))
                self.assertIn("pip", network_changes[0])
                self.assertIn("16384", limit_changes[0])

    def test_generated_readmes_contain_no_unresolved_or_stale_stdin_claim(self) -> None:
        stale_fragments = (
            "stdin snapshots remain disabled",
            "stdin snapshot 仍关闭",
            "stdin snapshot 仍關閉",
            "stdin snapshot reste désactivé",
            "stdin snapshot sigue desactivado",
            "stdin snapshot は無効",
            "stdin snapshot은 비활성",
            "stdin snapshot остается выключенным",
            "يظل stdin snapshot معطلا",
        )
        for code in LANGUAGE_CODES:
            with self.subTest(code=code):
                body = (README_DIR / f"README-{code}.md").read_text(encoding="utf-8")
                self.assertIn("1 MiB", body)
                self.assertIn("1.0-1.6", body)
                self.assertIn("`executionMode=long-running`", body)
                self.assertIn("15 s", body)
                self.assertIn("45 s", body)
                self.assertIn("2 min", body)
                self.assertIn("64 KiB", body)
                self.assertIn("16 MiB", body)
                self.assertIn("16384", body)
                self.assertIn("30 min", body)
                self.assertIn("64 MiB", body)
                self.assertIn("8192", body)
                self.assertIn("128 MiB", body)
                self.assertIn(".dist-info", body)
                self.assertIn("INTERNET", body)
                self.assertIn("SHA-256", body)
                self.assertIn("`toast`", body)
                self.assertIn("`files.read_text/write_text/exists/is_file/is_dir/list`", body)
                self.assertIn("dialogs.alert/confirm/prompt/select", body)
                self.assertIn("engines.current/run/stop_self", body)
                self.assertIn("automator.click/long_click/press/swipe/back/home", body)
                self.assertIn("selector.snapshot/find/click/set_text", body)
                self.assertIn("images.capture_screen", body)
                self.assertIn("images.find_color", body)
                self.assertIn("1000000", body)
                self.assertIn("4 s", body)
                self.assertIn("48 KiB", body)
                self.assertIn("256 Unicode code points", body)
                self.assertIn("1024 UTF-8 bytes", body)
                self.assertIn("SELECTOR_SCAN_LIMIT_EXCEEDED", body)
                self.assertIn("STALE_NODE", body)
                self.assertIn("SCREEN_CAPTURE_FAILED", body)
                self.assertIn("RESULT_LIMIT_EXCEEDED", body)
                self.assertIn("STALE_IMAGE", body)
                self.assertIn("16777216", body)
                self.assertIn("255", body)
                self.assertIn("32 KiB", body)
                self.assertIn("CapabilityUnavailableError", body)
                self.assertIn("NESTED_PYTHON_NOT_ALLOWED", body)
                self.assertIn("INTERACTIVE_NOT_ALLOWED", body)
                self.assertNotIn("{{", body)
                lowered = body.lower()
                for stale in stale_fragments:
                    self.assertNotIn(stale.lower(), lowered)

    def test_primary_generated_readmes_state_scoped_foreground_input_and_no_page_gate(self) -> None:
        simplified = (ROOT / "README.md").read_text(encoding="utf-8")
        english = (README_DIR / "README-en.md").read_text(encoding="utf-8")
        self.assertEqual(
            simplified,
            (README_DIR / "README-zh-Hans.md").read_text(encoding="utf-8"),
        )
        self.assertIn("协议 1.3 在快照 EOF 后为内置 `input()`", simplified)
        self.assertIn("`getpass.getpass()` 使用隐藏回显", simplified)
        self.assertIn("后台启动绝不打开输入 UI", simplified)
        self.assertIn("直接 `sys.stdin` 始终有限", simplified)
        self.assertIn("协议 1.4 增加显式严格 JSON 结果", simplified)
        self.assertIn("协议 1.5 增加绑定单次执行", simplified)
        self.assertIn("协议 1.6 增加显式 `long-running`", simplified)
        self.assertIn("`executionMode=long-running`", simplified)
        self.assertIn("`toast`", simplified)
        self.assertIn("`files.read_text/write_text/exists/is_file/is_dir/list`", simplified)
        self.assertIn("`dialogs.alert/confirm/prompt/select`", simplified)
        self.assertIn("`engines.current/run/stop_self`", simplified)
        self.assertIn("`automator.click/long_click/press/swipe/back/home`", simplified)
        self.assertIn("`selector.snapshot/find/click/set_text`", simplified)
        self.assertIn("`images.capture_screen`", simplified)
        self.assertIn("`images.find_color`", simplified)
        self.assertIn("0 到 1000000", simplified)
        self.assertIn("1 ms 到 4 s", simplified)
        self.assertIn("最多接受 128 个节点、深度 32 及 48 KiB JSON", simplified)
        self.assertIn("`SELECTOR_SCAN_LIMIT_EXCEEDED`", simplified)
        self.assertIn("`STALE_NODE`", simplified)
        self.assertIn("屏幕截图每次执行最多保留 1 张", simplified)
        self.assertIn("`SCREEN_CAPTURE_FAILED`", simplified)
        self.assertIn("`RESULT_LIMIT_EXCEEDED`", simplified)
        self.assertIn("`STALE_IMAGE`", simplified)
        self.assertIn("逐通道阈值", simplified)
        self.assertIn("项目本地纯 Python 包与 `.dist-info` 元数据", simplified)
        self.assertIn("项目 workspace 上限为压缩后 64 MiB、8192 个文件条目及解压后 128 MiB", simplified)
        self.assertIn("M4 路径 A 已完成", simplified)
        self.assertIn("`INTERACTIVE_NOT_ALLOWED`", simplified)
        self.assertIn("绝不被解析为结果", simplified)
        self.assertIn("API 37 x86_64 16 KB page 模拟器的聚焦冒烟", simplified)
        self.assertIn("不等同于完整兼容性 gate", simplified)
        self.assertIn("Protocol 1.3 adds Host-owned, foreground-only prompt/reply", english)
        self.assertIn("`getpass.getpass()` uses hidden echo", english)
        self.assertIn("background launches never open input UI", english)
        self.assertIn("Direct `sys.stdin` remains finite", english)
        self.assertIn("Protocol 1.4 adds explicit strict JSON", english)
        self.assertIn("Protocol 1.5 adds a pure-data Host capability broker", english)
        self.assertIn("Protocol 1.6 adds explicit `long-running`", english)
        self.assertIn("`executionMode=long-running`", english)
        self.assertIn("`toast`", english)
        self.assertIn("`files.read_text/write_text/exists/is_file/is_dir/list`", english)
        self.assertIn("`dialogs.alert/confirm/prompt/select`", english)
        self.assertIn("`engines.current/run/stop_self`", english)
        self.assertIn("`automator.click/long_click/press/swipe/back/home`", english)
        self.assertIn("`selector.snapshot/find/click/set_text`", english)
        self.assertIn("`images.capture_screen`", english)
        self.assertIn("`images.find_color`", english)
        self.assertIn("0 through 1000000", english)
        self.assertIn("1 ms through 4 s", english)
        self.assertIn("at most 128 nodes, depth 32, and 48 KiB of JSON", english)
        self.assertIn("`SELECTOR_SCAN_LIMIT_EXCEEDED`", english)
        self.assertIn("`STALE_NODE`", english)
        self.assertIn("Screen capture retains at most 1 image per execution", english)
        self.assertIn("`SCREEN_CAPTURE_FAILED`", english)
        self.assertIn("`RESULT_LIMIT_EXCEEDED`", english)
        self.assertIn("`STALE_IMAGE`", english)
        self.assertIn("per-channel threshold", english)
        self.assertIn("project-local pure-Python packages and `.dist-info` metadata", english)
        self.assertIn("64 MiB compressed, 8192 file entries, and 128 MiB extracted", english)
        self.assertIn("M4 Path A is complete", english)
        self.assertIn("`INTERACTIVE_NOT_ALLOWED`", english)
        self.assertIn("never parsed as a result", english)
        self.assertIn("API 37 x86_64 16 KB-page emulator smoke has passed", english)
        self.assertIn("not a comprehensive compatibility gate", english)


if __name__ == "__main__":
    unittest.main()
