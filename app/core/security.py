import bcrypt

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
