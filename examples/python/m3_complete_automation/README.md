# Complete Settings automation example

This project is the complete M3 workflow promised by the Roadmap:

1. launch the real Android Settings application with `app.launch`;
2. find its search control in a bounded accessibility snapshot;
3. click that retained node with `selector.click`;
4. verify the real Settings search destination;
5. capture `screens/settings-search.png` and assert its PNG header, IHDR CRC,
   dimensions, and exact agreement with the verified UI root bounds;
6. publish both the screenshot artifact and a strict structured result.

The script does not type a query or change any Settings value. If Android
resumes an existing Settings subpage, it uses at most four explicit Back actions
inside the known Settings task before looking for the homepage control again.
Every wait has a fixed deadline.

## Prerequisites

- AutoJs6 and this Python Runtime build must be paired and enabled.
- Android 11 or newer is required for accessibility screenshots.
- The AutoJs6 accessibility service must already be enabled and operational.
  The script never enables it or opens its configuration page.
- The resource IDs target the AOSP/Pixel Settings implementation used by the
  API 37 AutoJs6 emulator. Vendor Settings applications may use different
  packages or resource IDs; adjust the four constants at the top of `main.py`
  when running on such a device.

Copy the whole directory to AutoJs6 and run it as a Python project. A successful
run leaves the Settings search screen in front, prints each workflow checkpoint,
returns a structured success object, and exposes `screens/settings-search.png`
as an execution artifact.

The screenshot assertion deliberately checks structure and display dimensions,
not theme-specific pixel colors, so light/dark theme changes do not invalidate
the workflow.
