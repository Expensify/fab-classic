import threading
import sys

from fabric.state import env


def reraise(tp, value, tb=None):
    try:
        if value is None:
            value = tp()
        if value.__traceback__ is not tb:
            raise value.with_traceback(tb)
        raise value
    finally:
        value = None
        tb = None


class ThreadHandler(object):
    def __init__(self, name, callable, *args, **kwargs):
        # Set up exception handling
        self.exception = None

        # Capture the parent thread's env so child threads inherit it
        parent_env = env._local()

        def wrapper(*args, **kwargs):
            try:
                if parent_env is not None:
                    env._thread_local._data = parent_env
                callable(*args, **kwargs)
            except BaseException:
                self.exception = sys.exc_info()
            finally:
                if parent_env is not None:
                    env._clear_thread_local()
        # Kick off thread
        thread = threading.Thread(None, wrapper, name, args, kwargs)
        thread.setDaemon(True)
        thread.start()
        # Make thread available to instantiator
        self.thread = thread

    def raise_if_needed(self):
        if self.exception:
            e = self.exception
            reraise(e[0], e[1], e[2])
