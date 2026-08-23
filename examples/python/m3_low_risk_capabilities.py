"""Small, directly runnable example for the protocol 1.5 Host broker."""

from autojs6 import app, clip, result, toast


message = "Hello from AutoJs6 Python"
clip.set(message)
toast(f"Copied: {clip.get()}")

# Bringing the already-running Host to the foreground is a low-impact way to
# demonstrate package launching. A missing package returns False.
host_launched = app.launch("org.autojs.autojs6")

# These APIs intentionally perform visible external actions, so opt in by
# uncommenting a line and choosing a target appropriate for the device:
# app.launch_app("Browser")
# app.open_url("https://docs.autojs6.com")

result.set(
    {
        "clipboard": clip.get(),
        "hostLaunched": host_launched,
    }
)
