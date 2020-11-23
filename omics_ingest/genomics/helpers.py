from contextlib import contextmanager


@contextmanager
def cleanuping(thing):
    try:
        yield thing
    finally:
        thing.cleanup()
