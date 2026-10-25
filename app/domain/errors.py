"""Business-rule violations. Controllers catch DomainError and show the message."""


class DomainError(Exception):
    """Base class for every business-rule violation."""


class ValidationError(DomainError):
    """Input is missing or malformed."""


class NotFound(DomainError):
    """The requested record does not exist."""


class NotAllowed(DomainError):
    """The user may not do this (wrong hub, wrong owner)."""


class VoucherError(DomainError):
    """A voucher cannot be used for this order."""


class InvalidTransition(DomainError):
    """The order state machine does not allow this change."""


class HubFullError(DomainError):
    """The hub has reached its capacity and takes no new orders."""

    def __init__(self, message, suggestions=None):
        super().__init__(message)
        self.suggestions = suggestions or []
