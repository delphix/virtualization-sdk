
class LibraryError(Exception):
    """Plugin-catchable exception

    Some library errors (timeouts, host unreachable, etc.) are potentially
    actionable by plugin code. For example, they may choose to retry, or to
    raise their own plugin-specific exception.

    This exception will be thrown whenever a library call fails due to such an
    actionable error.

    Attributes:
    message - A localized user-readable message.
    """

    @property
    def message(self):
        return self.args[0]

    def __init__(self, id, message):
        self._id = id
        super(LibraryError, self).__init__(message)
