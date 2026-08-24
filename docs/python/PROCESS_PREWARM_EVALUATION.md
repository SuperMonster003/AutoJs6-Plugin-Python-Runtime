# M5 process-prewarm evaluation

Status: accepted on `QV710AF65F` on 2026-08-24. The measured median is
`429 ms`, below the `1000 ms` decision threshold, so process retention is not
justified. The runtime keeps its existing per-execution process retirement and
no execution-afterlife option is added.

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

## 2026-08-24 QV710AF65F result

The probe was run five times on an idle `QV710AF65F`, waiting for each run to
finish before starting the next. The accepted Host context remained
`afca7b14c`, versionCode `5276`; no Plugin package change was reported after the
preceding accepted versionCode `81` smoke.

| Run | `startup_probe_ms` | Plugin PID | Engine ID | Full Host duration |
| ---: | ---: | ---: | ---: | ---: |
| 1 | 441 ms | 26868 | 5 | 471 ms |
| 2 | 447 ms | 27018 | 6 | 475 ms |
| 3 | 429 ms | 27055 | 7 | 456 ms |
| 4 | 427 ms | 27091 | 8 | 452 ms |
| 5 | 428 ms | 27121 | 9 | 455 ms |

The sorted startup values are `427, 428, 429, 441, 447 ms`. Their arithmetic
mean is `434.4 ms`, the all-sample median is `429 ms`, and the median excluding
the first run is `428.5 ms`. The minimum is `427 ms`, the maximum is `447 ms`,
and the range is `20 ms`. The median full Host duration is `456 ms`.

All five Plugin PIDs are distinct, consistent with a fresh process generation
for every dispatched execution. Every startup value is below `1000 ms`, and
even the maximum has more than 50% headroom to the threshold. The evaluation is
therefore closed with decision **NO PROCESS RETENTION**: preserve deterministic
per-execution retirement, state isolation, and process-restart cancellation;
do not add a keep-process option, protocol field, or runtime-lifetime branch.

This is a focused device decision for the prewarm Roadmap item. It does not by
itself claim a complete device matrix, publication, or release qualification.
