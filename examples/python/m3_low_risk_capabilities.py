"""Small, directly runnable example for the protocol 1.5 Host broker."""

from autojs6 import app, clip, console, device, notice, result, toast
from autojs6.errors import HostCapabilityError


message = "Hello from AutoJs6 Python"
clip.set(message)
toast(f"Copied: {clip.get()}")

current = device.info()
console.log(f"Battery: {current['battery']['percent']}%")
console.warn(f"Screen brightness: {current['screen']['brightness']}")
console.error("This is an intentional error-level example line")

try:
    notice("AutoJs6 Python Host broker is ready")
    notice_status = "posted"
except HostCapabilityError as error:
    # Android 13+ permission or the app/channel switch may be disabled. The API
    # reports that state and never opens settings on the script's behalf.
    if error.code != "PERMISSION_DENIED":
        raise
    notice_status = error.code

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
        "device": current,
        "notice": notice_status,
    }
)
