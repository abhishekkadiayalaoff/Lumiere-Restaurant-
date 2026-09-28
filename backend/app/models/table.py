import enum
from sqlalchemy import Column, Integer, String, Enum
from app.db.base import Base


class TableStatus(str, enum.Enum):
    available = "available"
    occupied = "occupied"
    reserved = "reserved"


class RestaurantTable(Base):
    __tablename__ = "restaurant_tables"

    id = Column(Integer, primary_key=True, index=True)
    table_number = Column(String, unique=True, nullable=False)
    capacity = Column(Integer, default=2)
    status = Column(Enum(TableStatus), default=TableStatus.available)