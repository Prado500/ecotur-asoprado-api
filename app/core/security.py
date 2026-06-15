import os
from datetime import timedelta, datetime, timezone

import bcrypt # Hashing de contraseñas y verificación
import jwt # Tokenización JWT

SECRET_KEY = os.getenv("JWT_SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
VERIFICATION_TOKEN_EXPIRE_MINUTES = int(os.getenv("VERIFICATION_TOKEN_EXPIRE_MINUTES", "15"))

"""
    FÁBRICA DE HASHES
"""
def get_password_hash(password: str) -> str:
    """
    Toma la contraseña usada por el usuario en su registro, y:
    1. Convierte el string a bytes.
    2. Genera la sal automática.
    3. Hashea agregando la sal al resto del hash y devuelve un string decodificado para PostgreSQL, que es el que como tal
       se guarda en la base de datos.
    """
    pwd_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password=pwd_bytes, salt=salt)

    return hashed_password.decode('utf-8')

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Compara la contraseña plana con la que se intenta iniciar sesión con el hash de la base de datos.
    Ambos deben convertirse a bytes para que bcrypt pueda:
    1. Identificar y extraer la sal del hash de la base de datos.
    2. Hashear la contraseña plana usando la misma sal empleada en el hasheo de la contraseña que se usó al crearse la cuenta
    3. Comparar ambos hash y retornar True si coinciden, o False si no.
    """
    password_byte_enc = plain_password.encode('utf-8')
    hashed_password_bytes = hashed_password.encode('utf-8')

    return bcrypt.checkpw(password=password_byte_enc, hashed_password=hashed_password_bytes)

"""
    FÁBRICA DE TOKENS
"""
def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    """
    Fabrica el Json Web Token (JWT).
    Recibe los datos públicos (ej. {"sub": "manuel_ortigoza", "role": "tourist"})
    y le estampa la firma criptográfica usando la Llave Secreta.
    """
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp": expire})

    encoded_jwt = jwt.encode(payload=to_encode, key=SECRET_KEY, algorithm=ALGORITHM)

    return encoded_jwt

def create_verification_token(email: str) -> str:
    """
    Fabrica un JWT de un solo uso estrictamente para la verificación de identidad.
    Contiene un 'scope' específico para prevenir su uso como token de autorización general.
    """
    expire = datetime.now(timezone.utc) + timedelta(minutes=VERIFICATION_TOKEN_EXPIRE_MINUTES)

    to_encode = {
        "sub": email,
        "scope": "email_verification",
        "exp": expire
    }

    encoded_jwt = jwt.encode(payload=to_encode, key=SECRET_KEY, algorithm=ALGORITHM)

    return encoded_jwt