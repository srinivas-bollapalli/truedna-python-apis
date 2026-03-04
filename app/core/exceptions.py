class AppBaseError(Exception):
    """Base application error."""


class AuthError(AppBaseError):
    """Authentication / authorisation failure."""


class UserExistsError(AppBaseError):
    """Duplicate username or email."""


class NotFoundError(AppBaseError):
    """Requested resource not found."""
