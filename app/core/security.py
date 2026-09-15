import os
from datetime import timedelta, datetime, timezone

import bcrypt
import jwt

SECRET_KEY = os.getenv("JWT_SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
VERIFICATION_TOKEN_EXPIRE_MINUTES = int(os.getenv("VERIFICATION_TOKEN_EXPIRE_MINUTES", "15"))

"""
   HASH FACTORY
"""
def get_password_hash(password: str) -> str:
    """
    Performs the following operations using the given user password:

    1. Turns the string into bytes.
    2. Automatically generates the salt.
    3. Hashes and includes the salt to the hash. Then, it returns the decoded and salted password hash
       to be stored in the database.

    """
    pwd_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password=pwd_bytes, salt=salt)

    return hashed_password.decode('utf-8')

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Compares the raw password string against the hashed password.

    Bcrypt turns into bytes both the raw password entry and the hashed db password string in order to:

    1. Identify and extract the salt out of the db hashed password.
    2. Hash the raw entry using the retrieved salt.
    3. Compare if both  hashes match mathematically and return True if so,and false otherwise.
    """
    password_byte_enc = plain_password.encode('utf-8')
    hashed_password_bytes = hashed_password.encode('utf-8')

    return bcrypt.checkpw(password=password_byte_enc, hashed_password=hashed_password_bytes)

"""
    TOKEN FACTORY
"""
def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    """
    Generates a signed JWT token with an expiration date.

    It's given a payload (e.g. {"sub": "manuel_ortigoza", "role": "tourist"}), then
    checks weather there is a given parameter for the token lifespan and includes
    the expiration date within the payload. Afterward it produces the cryptographic
    signature using the secret key.
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
    Generates a single-use JWT token for user email validation purposes.

    There is a specific scope within the token's payload to prevent its usage as a
    general authorization token.

    """
    expire = datetime.now(timezone.utc) + timedelta(minutes=VERIFICATION_TOKEN_EXPIRE_MINUTES)

    to_encode = {
        "sub": email,
        "scope": "email_verification",
        "exp": expire
    }

    encoded_jwt = jwt.encode(payload=to_encode, key=SECRET_KEY, algorithm=ALGORITHM)

    return encoded_jwt