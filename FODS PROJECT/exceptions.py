
class LibraryError(Exception):
    """Base class for all custom exceptions in this system."""
    pass


class AuthenticationError(LibraryError):
    """Raised when login credentials are invalid."""
    pass


class AuthorizationError(LibraryError):
    """Raised when a user tries to perform an action their role does not allow."""
    pass


class BookNotFoundError(LibraryError):
    """Raised when a requested ISBN does not exist in the catalogue."""
    pass


class BookNotAvailableError(LibraryError):
    """Raised when a book is requested for borrowing but is already on loan."""
    pass


class MemberNotFoundError(LibraryError):
    """Raised when a member ID does not exist in the system."""
    pass


class DuplicateRecordError(LibraryError):
    """Raised when attempting to add a record (book/member) that already exists."""
    pass


class InvalidInputError(LibraryError):
    """Raised when user-supplied data fails validation (empty fields, bad dates, etc.)."""
    pass
