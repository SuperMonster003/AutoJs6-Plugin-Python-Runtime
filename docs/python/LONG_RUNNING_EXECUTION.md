# Protocol 1.6 long-running Python execution

Status: implemented on the current AutoJs6 Host and Python Runtime Plugin
source trees. Host API and focused Host/Plugin JVM tests pass offline. The
checked-in example and portable source checks are complete; this document does
not claim an Android device smoke, publication, or release acceptance.

## User selection

Long-running execution is an explicit Python project mode. Select it in
`project.json`:

```json
{
  "type": "python",
  "main": "main.py",
  "executionMode": "long-running"
}
```

An absent `executionMode`, or the exact value `bounded`, preserves bounded
execution. `long-running` and `timeout` are mutually exclusive: the Host rejects
a manifest which contains both instead of silently ignoring one. Standalone
`.py` files remain bounded because they have no admitted project declaration.

The long-running mode has no elapsed execution deadline. All existing resource
ceilings still apply, including output bytes/chunks, workspace size, interactive
input, structured results, artifacts, and Host capability call quotas. It also
retains the current single-active-session limit; protocol 1.6 is not concurrent
execution.

## Foreground-only authorization

The Host mints a one-use opaque grant only while a live foreground Activity is
handling an interactive user launch. The engine must consume that grant before
starting the Host-owned foreground service. A project declaration alone is not
authorization.

Scheduled tasks, background launches, plugin/developer launch paths, and Intent
launches receive the stable Host error `PYTHON_RUNTIME_LONG_RUNNING_NOT_ALLOWED`.
The Host never downgrades the request to bounded execution and never dispatches
it without the foreground lifetime.

## Protocol 1.6 extension

Protocol 1.6 keeps the existing AIDL session surface and appends one callback:
`IPythonExecutionCallback.onHeartbeat(byte[])`.

| Schema | Tag | Type | Meaning |
| --- | ---: | --- | --- |
| Capabilities (`0x50590002`) | 16 | optional `BOOLEAN` | `supportsLongRunningExecution`; absent means false |
| Execution request (`0x50590010`) | 17 | optional `INT32` | execution mode; absent means bounded (`1`), long-running is `2` |
| Execution heartbeat (`0x5059001c`) | 1 | `BYTES` | exact request UUID |
| Execution heartbeat (`0x5059001c`) | 2 | `INT64` | strictly ordered positive sequence |
| Execution heartbeat (`0x5059001c`) | 3 | `INT64` | monotonic elapsed milliseconds |

The Host omits request tag 17 for bounded execution, preserving protocol
1.0-1.5 request behavior. For long-running execution, tag 17 is marked
required-for-reader. An older reader therefore rejects the request instead of
silently applying a bounded or unknown policy. A protocol 1.6 Provider must
advertise long-running support, and a long-running request carries
`timeoutMillis=0`.

The Plugin emits the first heartbeat 15 seconds after `onStarted`, then every
15 seconds. Heartbeats share the ordered callback lane with output, input, and
the terminal callback. They stop on every terminal, cancellation, callback
death, or service-destruction path. A malformed, non-monotonic, undeliverable,
or unschedulable heartbeat retires the Plugin process rather than allowing an
unobserved execution to continue.

## Host foreground lifetime and liveness

For an admitted launch, AutoJs6 starts a dedicated, non-exported `specialUse`
foreground service and immediately promotes it with a low-importance persistent
notification. The notification names the Python project, shows elapsed time
after the first heartbeat, and exposes a Stop action. Stop reaches the owning
script engine, cancels the remote session, and uses the existing process-restart
cancellation contract; Python `finally` blocks are not guaranteed to run.

The Host independently enforces three monotonic leases:

- Provider `onStarted`: 2 minutes from controller creation;
- Provider heartbeat: 45 seconds after the latest accepted Provider signal;
- Host foreground-service pulse: 15 seconds, refreshed every 2 seconds.

Losing any lease, the bound Provider, the foreground service, or the Plugin
state fails closed with `PYTHON_RUNTIME_EXECUTION_LOST` and attempts remote
cancellation. The long-running service bind uses `BIND_IMPORTANT`; this improves
process importance but is not treated as proof of liveness.

Android 12 and newer restrict starting foreground services from the background,
which is why this mode requires a foreground user launch. Android 14 and newer
also require the declared foreground-service type and its matching permission;
the Host declares `specialUse`, `FOREGROUND_SERVICE`,
`FOREGROUND_SERVICE_SPECIAL_USE`, and the required subtype property. Android's
notification permission is not a prerequisite for starting a foreground
service, although notification visibility differs when the user denies it.

Official Android references:

- [Declare foreground services and request permissions](https://developer.android.com/develop/background-work/services/fgs/declare)
- [Foreground service types](https://developer.android.com/develop/background-work/services/fgs/service-types)
- [Launch a foreground service](https://developer.android.com/develop/background-work/services/fgs/launch)
- [Notification runtime permission](https://developer.android.com/develop/ui/compose/notifications/notification-permission)

## Compatibility and terminal behavior

- Bounded protocol 1.0-1.5 sessions remain byte-compatible and keep the current
  default/configured deadline capped by Provider policy (30 minutes today).
- Long-running execution requires a Host and Provider which both support
  protocol 1.6. Provider selection rejects an older or falsely advertising
  implementation before dispatch.
- Output remains credit-bounded. A script which prints indefinitely can still
  hit the negotiated output ceiling; long-running means no elapsed deadline,
  not unlimited memory or transport.
- There is still one terminal callback. Heartbeats cannot follow that terminal,
  and cancellation, timeout of a bounded session, Binder death, or a liveness
  failure is never automatically replayed.

## Manual smoke

Use [`examples/python/m5_long_running`](../../examples/python/m5_long_running).
Copy the directory as one AutoJs6 project and launch it from a foreground project
surface. Let it run for at least 60 seconds, confirm live console ticks and the
persistent notification/chronometer, then use the notification Stop action.
Finally run an ordinary bounded Python script to confirm that cancellation
retired and rebound the Plugin runtime cleanly.

Do not run this smoke through a scheduled task or Intent: rejection there is the
intended security behavior. Record the exact Host/Plugin APK identities and the
device API/ABI/page-size only when promoting the remaining Roadmap device item.
