"""Domain-level exceptions raised by the service layer and translated by global handlers."""


class DomainError(Exception):
    """
    Base class for every domain-level failure raised by the service layer.

    Carries a single human-readable detail so global handlers can expose it to
    API consumers, while transport semantics (HTTP status codes) remain the
    sole responsibility of the adapter layer.

    Attributes:
        detail (str): Human-readable explanation of the domain failure.
    """

    def __init__(self, detail: str):
        """
        Initializes the error with a human-readable failure explanation.

        Args:
            detail (str): Reason exposed to the API consumer.
        """
        self.detail = detail
        super().__init__(detail)


class AuthorizationError(DomainError):
    """
    Signals that an authenticated actor attempted a guarded operation without
    the required privileges.

    Raised exclusively by access-control policies so the service layer stays
    decoupled from the transport framework (FastAPI). A global exception
    handler maps this error to an HTTP 403 Forbidden response.

    Attributes:
        detail (str): Human-readable explanation of the authorization failure.
    """

    def __init__(self, detail: str = "No tiene los privilegios suficientes para realizar esta acción."):
        """
        Initializes the error with a human-readable failure explanation.

        Args:
            detail (str): Reason exposed to the API consumer. Defaults to a
                generic forbidden-access message.
        """
        super().__init__(detail)


class NotFoundError(DomainError):
    """
    Signals that a business entity required by the current operation does not
    exist (or was already logically removed) in the persistence layer.

    Raised by services before any authorization or mutation takes place, so
    existence checks (HTTP 404) always dominate privilege checks (HTTP 403).

    Attributes:
        detail (str): Human-readable explanation of the missing entity.
    """

    def __init__(self, detail: str):
        """
        Initializes the error with a human-readable failure explanation.

        Args:
            detail (str): Reason exposed to the API consumer.
        """
        super().__init__(detail)


class AlreadyExistsError(DomainError):
    """
    Signals that a uniqueness constraint was violated by the current operation
    (e.g. an email or cedula already registered).

    Raised by services whenever a duplicate entity is detected before
    persistence. The global handler maps it to an HTTP 400 Bad Request.

    Attributes:
        detail (str): Human-readable explanation of the duplicate entity.
    """

    def __init__(self, detail: str):
        """
        Initializes the error with a human-readable failure explanation.

        Args:
            detail (str): Reason exposed to the API consumer.
        """
        super().__init__(detail)


class InvalidCredentialsError(DomainError):
    """
    Signals that an authentication attempt failed (unknown email or password
    mismatch).

    Raised by the authentication business rule. The global handler maps it to
    an HTTP 401 Unauthorized response carrying the Bearer challenge header.

    Attributes:
        detail (str): Human-readable explanation of the authentication failure.
    """

    def __init__(self, detail: str):
        """
        Initializes the error with a human-readable failure explanation.

        Args:
            detail (str): Reason exposed to the API consumer.
        """
        super().__init__(detail)


class AccountNotActiveError(DomainError):
    """
    Signals that an authentication attempt targeted an account pending email
    verification or otherwise inactive.

    Raised by the authentication business rule after credentials were accepted.
    The global handler maps it to an HTTP 403 Forbidden response.

    Attributes:
        detail (str): Human-readable explanation of the inactive account.
    """

    def __init__(self, detail: str):
        """
        Initializes the error with a human-readable failure explanation.

        Args:
            detail (str): Reason exposed to the API consumer.
        """
        super().__init__(detail)


class InvalidVerificationTokenError(DomainError):
    """
    Signals that an email-verification token is invalid, expired or carries an
    unexpected scope.

    Raised by the email verification business rule for any token defect that
    prevents account activation. The global handler maps it to an HTTP 400
    Bad Request response.

    Attributes:
        detail (str): Human-readable explanation of the token defect.
    """

    def __init__(self, detail: str):
        """
        Initializes the error with a human-readable failure explanation.

        Args:
            detail (str): Reason exposed to the API consumer.
        """
        super().__init__(detail)
