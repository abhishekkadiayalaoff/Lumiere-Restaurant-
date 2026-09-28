import enum
from sqlalchemy import Column, Integer, String, Boolean, Enum
from app.db.base import Base


class UserRole(str, enum.Enum):
    admin = "admin"
    customer = "customer"
    chef = "chef"
    waiter = "waiter"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    phone = Column(String, nullable=True)
    hashed_password = Column(String, nullable=False)
    role = Column(Enum(UserRole), default=UserRole.customer)
    is_active = Column(Boolean, default=True)