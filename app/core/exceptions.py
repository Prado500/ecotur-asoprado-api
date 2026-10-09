"""Domain-level exceptions raised by the service layer and translated by global handlers."""


class AuthorizationError(Exception):
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
        self.detail = detail
        super().__init__(detail)
