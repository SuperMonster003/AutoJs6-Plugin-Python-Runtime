NAME = "B"

from . import cycle_a


def sees_a() -> str:
    return cycle_a.NAME
