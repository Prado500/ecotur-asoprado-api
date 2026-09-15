from pydantic import BaseModel

class TokenResponse(BaseModel):
    """
    Schema responsible for the standard server response after a successful login operation.
    Complies with the OAuth2 standard
    """
    access_token: str
    token_type: str = "bearer"

class TokenData(BaseModel):
    """
    Schema responsible for payload-contained information validation.

    Employed to verify a user's email complies to be a valid one before
    performing a query to confirm weather such user is active and allowed
    within the get_current_user() endpoint access control function.
    """
    email: str | None = None
    role: str | None = None