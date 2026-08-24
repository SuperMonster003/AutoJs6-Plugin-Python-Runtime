"""Keep running until the Host notification Stop action cancels this process."""

import time


started_at = time.monotonic()
tick = 0
print("M5 long-running smoke started; stop it from the AutoJs6 notification.", flush=True)

while True:
    elapsed = time.monotonic() - started_at
    print(f"tick={tick} elapsed={elapsed:.1f}s", flush=True)
    tick += 1
    time.sleep(5)
