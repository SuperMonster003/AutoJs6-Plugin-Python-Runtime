"""Print only after first.py releases the Host FIFO admission slot."""

import os
import time


print(f"second admitted pid={os.getpid()} at={time.time_ns()}", flush=True)
print("second finished", flush=True)
