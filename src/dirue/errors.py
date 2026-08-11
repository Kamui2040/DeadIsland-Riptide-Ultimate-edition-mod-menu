"""Project-specific exceptions."""


class DirueError(Exception):
    """Base exception for expected DIRUE failures."""


class ValidationError(DirueError):
    """Raised when an installation, archive, or patch precondition is invalid."""


class PatchError(DirueError):
    """Raised when a semantic patch cannot be applied unambiguously."""
