from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.db.database import get_db
from app.models.user import User, UserRole
from app.schemas.user import UserCreate, UserResponse
from app.core.security import get_password_hash

router = APIRouter()


@router.post("/registro", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def registrar_turista(usuario: UserCreate, db: AsyncSession = Depends(get_db)):
    """
    Endpoint público para que los turistas creen su cuenta en ASOPRADO.
    Contribuye a resolver la HU-01.
    """

    stmt = select(User).where(User.email == usuario.email)
    resultado = await db.execute(stmt)
    usuario_existente = resultado.scalars().first()
    if usuario_existente:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Este correo electrónico ya se encuentra registrado."
        )

    hashed_password = get_password_hash(usuario.password)

    nuevo_usuario = User(
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
