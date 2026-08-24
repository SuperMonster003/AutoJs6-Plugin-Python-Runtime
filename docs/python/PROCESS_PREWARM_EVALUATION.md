# M5 process-prewarm evaluation

Status: the measurement path is implemented without changing protocol or
runtime lifetime. Physical-device samples are still required before deciding
whether to add an execution-afterlife option.

## Product metric

The decision metric is user-visible launch-to-first-Python latency, not an
isolated CPython interpreter microbenchmark. The probe captures wall-clock time
at the first practical Python statement, then obtains the Host engine's existing
`startedAtMillis` through `autojs6.engines.current()` and subtracts the two.

This interval deliberately includes the work a user waits for before Python can
run: Host engine setup, the global FIFO when idle, source/workspace snapshot,
Provider process launch and binding, input validation, Chaquopy startup, and
initial standard-library import. The broker call itself happens after the first
timestamp is captured, so it does not inflate the result.

The value is unsuitable when another Python execution is active or queued,
because FIFO wait would dominate it. It also uses Android wall-clock time on
both sides, so a manual system-clock change during the short launch interval
invalidates that sample.

## Why measurement comes first

The current process-per-execution model gives strong and simple semantics:

- cancellation retires the complete CPython process;
- `sys.modules`, `sys.path`, current directory, stdio, import caches, patched
  input functions, extension state, and user-created threads cannot leak into a
  later execution;
- the Host FIFO hands each waiter a fresh runtime generation.

Keeping the process alive after terminal would trade those properties for
latency. No such trade is justified until the physical-device median exceeds
the Roadmap threshold.

## Physical-device procedure

Use [`examples/python/m5_startup_probe`](../../examples/python/m5_startup_probe)
on an idle Host:

1. Ensure no other Python script is active or queued.
2. Run the project five times, waiting for each result and process retirement
   before starting the next run.
3. Record every `startup_probe_ms` and `plugin_pid` line. A fresh PID is expected
   for each dispatched execution, subject to ordinary Android PID reuse.
4. Keep the first value separate because Android filesystem/page caches may make
   it visibly colder than later process launches. Compute the median of all five
   values and also report the four-value median excluding the first sample.

Decision rule:

- median at or below 1000 ms: retain per-execution retirement and close prewarm
  as not justified;
- median above 1000 ms: design an explicit opt-in "keep process after execution"
  mode, then measure it with the same probe before accepting the added state-
  contamination risk;
- invalid, negative, queued, or interrupted samples are discarded and rerun.

This probe does not itself claim a device result, a warm-process implementation,
or a release qualification.
