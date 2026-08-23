"""M3 bounded Host accessibility actions.

Set the coordinates below for the target device, then opt in before running this example. Global
Back and Home have a separate opt-in because they change the foreground screen.
"""

from autojs6 import automator, result


TARGET_X = 540
TARGET_Y = 1200
RUN_COORDINATE_ACTIONS = False
RUN_GLOBAL_ACTIONS = False


outcome = {}

if RUN_COORDINATE_ACTIONS:
    outcome.update(
        {
            "click": automator.click(TARGET_X, TARGET_Y),
            "longClick": automator.long_click(TARGET_X, TARGET_Y),
            "press": automator.press(TARGET_X, TARGET_Y, duration_ms=100),
            "swipe": automator.swipe(
                TARGET_X,
                TARGET_Y + 300,
                TARGET_X,
                TARGET_Y,
                duration_ms=300,
            ),
        }
    )

if RUN_GLOBAL_ACTIONS:
    outcome["back"] = automator.back()
    outcome["home"] = automator.home()

result.set(outcome)
