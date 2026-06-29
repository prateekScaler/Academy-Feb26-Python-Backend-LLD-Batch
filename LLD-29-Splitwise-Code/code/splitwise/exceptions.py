class SplitwiseError(Exception):
    """Base for all domain errors."""


class SplitError(SplitwiseError):
    """The shares don't sum to the total, or the split args are invalid."""


class PermissionDenied(SplitwiseError):
    """The caller isn't allowed to perform this action (authorisation)."""
