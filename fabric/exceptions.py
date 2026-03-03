"""
Custom Fabric exception classes.

Most are simply distinct Exception subclasses for purposes of message-passing
(though typically still in actual error situations.)
"""


class NetworkError(Exception):
    # Must allow for calling with zero args/kwargs for consistency.
    def __init__(self, message, wrapped):
        self.message = message
        self.wrapped = wrapped

    def __str__(self):
        return self.message or ""

    def __repr__(self):
        return "%s(%s) => %r" % (
            self.__class__.__name__, self.message, self.wrapped
        )


class CommandTimeout(Exception):
    def __init__(self, timeout):
        self.timeout = timeout

        message = 'Command failed to finish in %s seconds' % (timeout)
        self.message = message
        super(CommandTimeout, self).__init__(message)
