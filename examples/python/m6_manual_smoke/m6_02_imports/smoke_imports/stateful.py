COUNTER = 0


def claim_first_import() -> int:
    global COUNTER
    COUNTER += 1
    return COUNTER
