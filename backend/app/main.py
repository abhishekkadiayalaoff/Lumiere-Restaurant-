from fastapi import FastAPI

from app.db.base import Base
from app.db.session import engine
from app.models import User, MenuItem, Order
from app.api.router import api_router
from app.models import User, MenuItem, Order, CartItem
from app.models import User, MenuItem, Order, OrderItem, CartItem
from app.models import User, MenuItem, Order, OrderItem, CartItem, RestaurantTable
from app.models import User, MenuItem, Order, OrderItem, CartItem, RestaurantTable, Payment


Base.metadata.create_all(bind=engine)

app = FastAPI(title="Lumiere Restaurant API")

app.include_router(api_router, prefix="/api/v1")


@app.get("/")
def root():
    return {
        "status": "ok",
        "message": "Lumiere Restaurant API is running"
    }