"""Hold the Host's single Python admission slot long enough to queue another run."""

import os
import time


print(f"first admitted pid={os.getpid()}", flush=True)
for tick in range(1, 16):
    print(f"first tick={tick}", flush=True)
    time.sleep(1)
print("first finished", flush=True)
