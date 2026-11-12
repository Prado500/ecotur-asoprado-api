from datetime import UTC, datetime, timedelta

import bcrypt
import jwt

from app.core.config import get_settings

"""
   HASH FACTORY
"""


def get_password_hash(password: str) -> str:
    """Performs the following operations using the given user password.

    1. Turns the string into bytes.
    2. Automatically generates the salt.
    3. Hashes and includes the salt to the hash. Then, it returns the decoded and salted password
       hash to be stored in the database.

    """
    pwd_bytes = password.encode("utf-8")
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password=pwd_bytes, salt=salt)

    return hashed_password.decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Compares the raw password string against the hashed password.

    Bcrypt turns into bytes both the raw password entry and the hashed db password string
    in order to:

    1. Identify and extract the salt out of the db hashed password.
    2. Hash the raw entry using the retrieved salt.
    3. Compare if both  hashes match mathematically and return True if so,and false otherwise.
    """
    password_byte_enc = plain_password.encode("utf-8")
    hashed_password_bytes = hashed_password.encode("utf-8")

    return bcrypt.checkpw(password=password_byte_enc, hashed_password=hashed_password_bytes)


"""
    TOKEN FACTORY
"""

# Value of the scope claim of each token kind. The values travel in tokens already issued:
# changing one invalidates them.
ACCESS_TOKEN_SCOPE = "access"
EMAIL_VERIFICATION_SCOPE = "email_verification"


def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    """Generates a signed JWT token with an expiration date.

    It's given a payload (e.g. {"sub": "manuel_ortigoza", "role": "tourist"}), then
    checks weather there is a given parameter for the token lifespan and includes
    the expiration date within the payload. Afterward it produces the cryptographic
    signature using the secret key and algorithm of the application settings.

    The scope claim is always ACCESS_TOKEN_SCOPE, over any scope in data: no caller
    chooses it, as create_verification_token fixes its own.

    Args:
        data (dict): Claims to sign; copied, never mutated. A scope in it is replaced.
        expires_delta (timedelta | None): Token lifespan. When missing, the settings'
            access_token_expire_minutes applies.

    Returns:
        str: The encoded and signed JWT.
    """
    settings = get_settings()
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.now(UTC) + expires_delta
    else:
        expire = datetime.now(UTC) + timedelta(minutes=settings.access_token_expire_minutes)

    to_encode.update({"scope": ACCESS_TOKEN_SCOPE, "exp": expire})

    encoded_jwt = jwt.encode(
        payload=to_encode, key=settings.jwt_secret_key, algorithm=settings.algorithm
    )

    return encoded_jwt


def create_verification_token(email: str) -> str:
    """Generates a single-use JWT token for user email validation purposes.

    There is a specific scope within the token's payload to prevent its usage as a
    general authorization token. Its lifespan is the settings'
    verification_token_expire_minutes.

    Args:
        email (str): Address of the account to verify; becomes the sub claim.

    Returns:
        str: The encoded and signed verification JWT.
    """
    settings = get_settings()
    expire = datetime.now(UTC) + timedelta(minutes=settings.verification_token_expire_minutes)

    to_encode = {"sub": email, "scope": EMAIL_VERIFICATION_SCOPE, "exp": expire}

    encoded_jwt = jwt.encode(
        payload=to_encode, key=settings.jwt_secret_key, algorithm=settings.algorithm
    )

    return encoded_jwt
