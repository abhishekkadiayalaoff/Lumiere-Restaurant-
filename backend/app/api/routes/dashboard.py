from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.db.session import get_db
from app.models.user import User
from app.models.menu_item import MenuItem
from app.models.order import Order, OrderStatus

router = APIRouter()


@router.get("/admin")
def admin_dashboard(db: Session = Depends(get_db)):
    total_sales = db.query(func.sum(Order.total_amount)).scalar() or 0

    return {
        "dashboard": "admin",
        "total_users": db.query(User).count(),
        "total_menu_items": db.query(MenuItem).count(),
        "total_orders": db.query(Order).count(),
        "pending_orders": db.query(Order).filter(Order.status == OrderStatus.pending).count(),
        "accepted_orders": db.query(Order).filter(Order.status == OrderStatus.accepted).count(),
        "preparing_orders": db.query(Order).filter(Order.status == OrderStatus.preparing).count(),
        "ready_orders": db.query(Order).filter(Order.status == OrderStatus.ready).count(),
        "delivered_orders": db.query(Order).filter(Order.status == OrderStatus.delivered).count(),
        "total_sales": total_sales
    }


@router.get("/customer/{customer_id}")
def customer_dashboard(customer_id: int, db: Session = Depends(get_db)):
    orders = db.query(Order).filter(Order.customer_id == customer_id).all()

    return {
        "dashboard": "customer",
        "customer_id": customer_id,
        "available_menu_items": db.query(MenuItem).filter(MenuItem.is_available == True).all(),
        "my_orders": orders,
        "total_orders": len(orders)
    }


@router.get("/chef")
def chef_dashboard(db: Session = Depends(get_db)):
    kitchen_orders = db.query(Order).filter(
        Order.status.in_([
            OrderStatus.accepted,
            OrderStatus.preparing
        ])
    ).all()

    return {
        "dashboard": "chef",
        "kitchen_orders": kitchen_orders,
        "total_kitchen_orders": len(kitchen_orders)
    }


@router.get("/waiter")
def waiter_dashboard(db: Session = Depends(get_db)):
    ready_orders = db.query(Order).filter(
        Order.status == OrderStatus.ready
    ).all()

    return {
        "dashboard": "waiter",
        "ready_orders": ready_orders,
        "total_ready_orders": len(ready_orders)
    }