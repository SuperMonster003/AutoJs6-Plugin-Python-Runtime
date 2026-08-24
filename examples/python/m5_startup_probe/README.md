# M5 Python startup probe

This bounded project measures user-visible time from Host engine start to the
first practical Python statement. It does not keep the runtime process alive or
change execution semantics.

Run the project five times while no other Python execution is active or queued.
Wait for each run to finish before starting the next. Record lines shaped like:

```text
startup_probe_ms=742 plugin_pid=12345 engine_id=17
```

Report all five `startup_probe_ms` values and PIDs. The M5 decision uses the
five-value median, with 1000 ms as the threshold for investigating an explicit
process-retention option. Also report the median excluding the first run because
Android page caches can make the first launch unusually cold.

Every dispatched run currently uses a fresh Plugin process generation. PID
reuse is possible, so a repeated number alone is not evidence of process reuse;
the Host/Plugin lifetime contract remains authoritative.
