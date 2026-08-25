NAME = "A"

from . import cycle_b


def chain() -> str:
    return NAME + cycle_b.NAME
