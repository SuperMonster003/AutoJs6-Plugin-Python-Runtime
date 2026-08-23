"""Inspect the active UI and optionally act on explicitly named controls."""

from autojs6 import result, selector


# Replace these exact strings with controls from the foreground application.
BUTTON_TEXT = "Example submit"
INPUT_DESCRIPTION = "Example input"

tree = selector.snapshot()
button = selector.find(text=BUTTON_TEXT, clickable=True)
editor = selector.find(description=INPUT_DESCRIPTION, editable=True)

clicked = selector.click(button) if button is not None else False
text_set = selector.set_text(editor, "Hello from Python") if editor is not None else False

result.set(
    {
        "schema": tree["schema"],
        "nodeCount": len(tree["nodes"]),
        "truncated": tree["truncated"],
        "buttonFound": button is not None,
        "inputFound": editor is not None,
        "clicked": clicked,
        "textSet": text_set,
    }
)
