import sys

from contextlib import contextmanager

class DevNull:
    def write(self, _):
        pass

    def flush(self):
        pass

@contextmanager
def no_stderr():
    save_stderr = sys.stderr
    sys.stderr = DevNull()
    try:
        yield
    finally:
        sys.stderr = save_stderr
