from pydantic import BaseModel


class MessageResponse(BaseModel):
    """Body of the routes that answer with a success flag and a message to show (BE-64).

    Declared on BaseModel with no validators: an output DTO never re-applies input rules
    (backlog A9). The shape is not specific to users, so it lives in its own module.

    Attributes:
        success: Whether the request was handled.
        message: Text for the end user.
    """

    success: bool
    message: str
