# Long-running foreground example

This is the smallest M5 long-running project. Its `project.json` explicitly
selects `"executionMode": "long-running"` and intentionally has no `timeout`.
`main.py` prints one live console tick every five seconds until the Host stops
the execution.

## Run it

1. Pair and enable compatible protocol 1.6 AutoJs6 and Python Runtime builds.
2. Copy this whole directory into AutoJs6 as a Python project.
3. While AutoJs6 is in the foreground, launch the project from an interactive
   project surface.
4. Confirm the persistent Python notification and live console ticks. After at
   least 60 seconds, use the notification Stop action.
5. Run an ordinary bounded Python script and confirm that the runtime rebinds
   cleanly after the stop-induced process restart.

Scheduled tasks, background/Intent launches, and developer-plugin launch paths
are intentionally rejected for this mode. If Android notification permission is
denied, the foreground service can still run, but Android may show it only in
the active-app/task-manager surface rather than the notification drawer.

Stopping is process-restart cancellation, not a cooperative Python exception.
Do not rely on `finally`, `atexit`, or buffered output for critical persistence.
All normal resource limits remain active, especially the finite output ceiling;
this example's five-second interval is for a short smoke, not an unattended
production logging policy.
