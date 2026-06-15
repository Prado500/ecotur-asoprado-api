from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.sql.operators import or_

from app.db.database import get_db
from app.models.user import User, UserRole
from app.schemas.user import UserCreate, UserResponse, UserLogin
from app.schemas.token import TokenResponse
from app.core.security import get_password_hash, verify_password, create_access_token
from app.api.dependencies import get_current_user

router = APIRouter()


@router.post("/registro", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def registrar_turista(usuario: UserCreate, db: AsyncSession = Depends(get_db)):
    """
    Endpoint público para que los turistas creen su cuenta en ASOPRADO.
    Contribuye a resolver la HU-01.
    """

    stmt = select(User).where(
        or_(
        User.cedula == usuario.cedula,
        User.email == usuario.email
    )
    )
    resultado = await db.execute(stmt)
    usuario_existente = resultado.scalars().first()
    if usuario_existente:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Este usuario ya se encuentra registrado."
        )

    hashed_password = get_password_hash(usuario.password)

    nuevo_usuario = User(
        cedula = usuario.cedula,
        email=usuario.email,
        first_name=usuario.first_name,
        last_name=usuario.last_name,
        phone=usuario.phone,
        password_hash=hashed_password,
        role=UserRole.tourist,
        data_consent=usuario.data_consent
    )

    db.add(nuevo_usuario)
    await db.commit()
    await db.refresh(
        nuevo_usuario)  # Se forza refrescar la sesión para obtener valores generados por el SGBD (los campos id y created_at)


    return nuevo_usuario

@router.post("/login", response_model=TokenResponse)
async def login(credenciales: UserLogin, db: AsyncSession = Depends(get_db)):
    """
    Endpoint para que los usuarios (Turistas o Admins) inicien sesión.
    Cumple con los criterios de la HU-02.
    """

    stmt = select(User).where(
        User.email == credenciales.email,
        User.is_active == True,
        User.deleted_at.is_(None)
    )
    resultado = await db.execute(stmt)
    usuario = resultado.scalars().first()



    if not usuario or not verify_password(credenciales.password, usuario.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Revise su correo y contraseña",
            headers={"WWW-Authenticate": "Bearer"},
        )


    datos_para_token = {
        "sub": usuario.email,
        "role": usuario.role.value
    }

    token_generado = create_access_token(data=datos_para_token)


    return {
        "access_token": token_generado,
        "token_type": "bearer"
    }

@router.get("/mi-perfil", response_model=UserResponse)
async def ver_mi_perfil(usuario_actual =  Depends(get_current_user)):

    """
    Endpoint que permite visualizar la información de un usuario (excluyendo hash de contraseña).
    :param usuario_actual: un User retornado por get_current_user().
    :return: User, cuya respuesta se sirve con UserResponse
    """

    return usuario_actual

