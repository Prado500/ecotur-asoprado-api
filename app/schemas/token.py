from pydantic import BaseModel

class TokenResponse(BaseModel):
    """
    Schema que define la respuesta estándar del servidor tras un login exitoso.
    Sigue el estándar OAuth2.
    """
    access_token: str
    token_type: str = "bearer"

class TokenData(BaseModel):
    """
    Schema interno para representar los datos contenidos dentro del Payload del JWT.
    Se usa para la posterior validación y extracción de información del turista.
    """
    email: str | None = None
    role: str | None = None