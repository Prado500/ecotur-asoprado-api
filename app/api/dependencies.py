import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.db.database import get_db
from app.models.user import User
from app.schemas.token import TokenData
from app.core.security import SECRET_KEY, ALGORITHM


# OAuth2PasswordBearer busca automáticamente en el scope el header "Authorization: Bearer <token>"
# Si no lo encuentra, arroja un error 401 forbidden.
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="usuarios/login")

async def get_current_user(
        token: str = Depends(oauth2_scheme),
        db: AsyncSession = Depends(get_db)
) -> User:
    """
    Esta función verifica la validez de los JWT de acuerdo a su firma y tiempo de expiración.
    Se inyecta en cualquier endpoint protegido. Además de Validar la firma del token y su fecha de expiración,
    Verifica que el payload del token sea coherente y que el usuario aún exista en la base de datos antes de retornarlo.

    Retorna y proporciona a cada endpoint protegido un User listo para ejecutar consultas en la bd.
    """
    credenciales_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No se pudo validar la autenticidad de sus credenciales",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        # jwt.decode verifica la firma matemática y revisa automáticamente si la fecha 'exp' ya pasó.
        # Si la firma del token proporcionado coincide con la calculada usando la llave secreta,
        # Entonces en payload se guarda un diccionario de python que contiene el payload del token {"sub", "role", "exp"}.
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

        email: str = payload.get("sub")
        if email is None:
            raise credenciales_exception # Si se intenta usar un token con firma auténtica pero payload incoherente (sin e-mail), se levanta la excepción.


        token_data = TokenData(email=email)

    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Su sesión ha expirado. Por favor, inicie sesión nuevamente.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.InvalidTokenError:
        # Excepción si la firma criptográfica no es auténtica.
        raise credenciales_exception


    # Puede ocurrir que un usuario reciba un token válido, y después sea eliminado antes que expire la sesión de dicho token suyo.
    # Aquí se realiza consulta en bd y solo traerá un resultado si el usuario con el token válido todavía está activo en el sistema.
    stmt = select(User).where(
        User.email == token_data.email,
        User.is_active == True,
        User.deleted_at.is_(None)
    )
    resultado = await db.execute(stmt)
    usuario = resultado.scalars().first()

    if usuario is None:
        raise credenciales_exception # Si el usuario fue eliminado, o está inactivo, se levanta la excepción.,


    return usuario