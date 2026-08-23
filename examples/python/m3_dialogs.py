"""Exercise the foreground-only AutoJs6 Host dialog capabilities."""

from autojs6 import dialogs, result


dialogs.alert("This dialog is rendered by the AutoJs6 Host.")

confirmed = dialogs.confirm("Continue with a prompt?", title="Host dialog demo")
name = (
    dialogs.prompt("What should Python call you?", default="AutoJs6 user")
    if confirmed
    else None
)
choice = dialogs.select(
    ["Keep exploring", "Finish the demo"],
    title="Choose the next step",
)

result.set(
    {
        "confirmed": confirmed,
        "name": name,
        "selection": choice,
    }
)
