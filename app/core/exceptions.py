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
