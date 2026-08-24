# Host FIFO concurrency example

These two bounded scripts demonstrate M5 concurrent admission without claiming
parallel CPython execution.

Run `first.py`, then run `second.py` while the first script is still ticking.
The second script is submitted immediately but must not print until the first
prints `first finished`. The paired Host keeps one active owner and up to 32
FIFO waiters; queued scripts do not bind the Plugin or consume their Provider
execution timeout.

The two printed Plugin PIDs should normally differ because each dispatched
execution retires its dedicated runtime process before the next waiter is
admitted. PID reuse is an operating-system detail, so output ordering and clean
automatic handoff are the authoritative observations.

Stopping `second.py` while it waits is an additional smoke: it must never print
`second admitted`, must not stop `first.py`, and must not block a later launch.
No Android device smoke is claimed by merely compiling these example files.
