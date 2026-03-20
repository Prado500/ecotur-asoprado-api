import enum
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum
from sqlalchemy.sql import func
from app.db.database import Base

"""
Se decide crear y aplicar tipos enumerados de acuerdo a los roles existentes para garantizar
consistencia y coherencia a nivel de la información que
persiste en la base de datos.
"""


class UserRole(str, enum.Enum):
    admin = "admin"
    tourist = "tourist"


"""
Definición de las clases modelo; estas delimitan la metadata que SQLAlchemy creará y utilizará
para generar y enviar a ejecutar al SGBD el código SQL plano que crea per sé las tablas en la base de datos.
"""


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(150), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    phone = Column(String(20), nullable=True)
    role = Column(Enum(UserRole), nullable=False, default=UserRole.tourist)
    data_consent = Column(Boolean, nullable=False, default=False)
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    deleted_at = Column(DateTime(timezone=True), nullable=True)
