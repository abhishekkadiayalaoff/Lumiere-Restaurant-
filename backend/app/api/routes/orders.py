from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.cart import CartItem
from app.models.menu_item import MenuItem
from app.models.order import Order, OrderItem, OrderStatus

router = APIRouter()


@router.post("/place")
def place_order(
    customer_id: int,
    table_number: str = "",
    db: Session = Depends(get_db)
):
    cart_items = db.query(CartItem).filter(
        CartItem.customer_id == customer_id
    ).all()

    if not cart_items:
        raise HTTPException(status_code=400, detail="Cart is empty")

    total_amount = 0

    order = Order(
        customer_id=customer_id,
        table_number=table_number,
        status=OrderStatus.pending,
        total_amount=0
    )

    db.add(order)
    db.commit()
    db.refresh(order)

    for cart_item in cart_items:
        menu_item = db.query(MenuItem).filter(
            MenuItem.id == cart_item.menu_item_id
        ).first()

        if not menu_item:
            continue

        total_amount += menu_item.price * cart_item.quantity

        order_item = OrderItem(
            order_id=order.id,
            menu_item_id=menu_item.id,
            quantity=cart_item.quantity,
            price=menu_item.price
        )

        db.add(order_item)

    order.total_amount = total_amount
    db.query(CartItem).filter(CartItem.customer_id == customer_id).delete()

    db.commit()
    db.refresh(order)

    return {
        "message": "Order placed successfully",
        "order_id": order.id,
        "total_amount": order.total_amount,
        "status": order.status
    }


@router.get("/")
def get_orders(db: Session = Depends(get_db)):
    return db.query(Order).all()


@router.get("/{order_id}")
def get_order(order_id: int, db: Session = Depends(get_db)):
    order = db.query(Order).filter(Order.id == order_id).first()

    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    items = db.query(OrderItem).filter(OrderItem.order_id == order_id).all()

    return {
        "order": order,
        "items": items
    }


@router.patch("/{order_id}/status")
def update_order_status(
    order_id: int,
    status: OrderStatus,
    db: Session = Depends(get_db)
):
    order = db.query(Order).filter(Order.id == order_id).first()

    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    allowed_transitions = {
        OrderStatus.pending: [OrderStatus.accepted, OrderStatus.cancelled],
        OrderStatus.accepted: [OrderStatus.preparing, OrderStatus.cancelled],
        OrderStatus.preparing: [OrderStatus.ready],
        OrderStatus.ready: [OrderStatus.served, OrderStatus.delivered],
        OrderStatus.served: [OrderStatus.delivered],
        OrderStatus.delivered: [],
        OrderStatus.cancelled: []
    }

    current_status = order.status

    if status not in allowed_transitions[current_status]:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid status change: {current_status} to {status}"
        )

    order.status = status
    db.commit()
    db.refresh(order)

    return {
        "message": "Order status updated",
        "order_id": order.id,
        "old_status": current_status,
        "new_status": order.status
    }