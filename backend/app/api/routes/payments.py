from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.order import Order
from app.models.payment import Payment, PaymentMethod, PaymentStatus

router = APIRouter()


@router.post("/")
def create_payment(
    order_id: int,
    method: PaymentMethod = PaymentMethod.cash,
    transaction_id: str = "",
    db: Session = Depends(get_db)
):
    order = db.query(Order).filter(Order.id == order_id).first()

    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    existing_payment = db.query(Payment).filter(
        Payment.order_id == order_id
    ).first()

    if existing_payment:
        raise HTTPException(status_code=400, detail="Payment already exists for this order")

    payment = Payment(
        order_id=order.id,
        amount=order.total_amount,
        method=method,
        status=PaymentStatus.pending,
        transaction_id=transaction_id
    )

    db.add(payment)
    db.commit()
    db.refresh(payment)

    return payment


@router.get("/")
def get_payments(db: Session = Depends(get_db)):
    return db.query(Payment).all()


@router.get("/{payment_id}")
def get_payment(payment_id: int, db: Session = Depends(get_db)):
    payment = db.query(Payment).filter(Payment.id == payment_id).first()

    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")

    return payment


@router.patch("/{payment_id}/status")
def update_payment_status(
    payment_id: int,
    status: PaymentStatus,
    db: Session = Depends(get_db)
):
    payment = db.query(Payment).filter(Payment.id == payment_id).first()

    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")

    payment.status = status
    db.commit()
    db.refresh(payment)

    return {
        "message": "Payment status updated",
        "payment_id": payment.id,
        "status": payment.status
    }