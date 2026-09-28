from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.cart import CartItem
from app.models.menu_item import MenuItem

router = APIRouter()


@router.post("/add")
def add_to_cart(
    customer_id: int,
    menu_item_id: int,
    quantity: int = 1,
    db: Session = Depends(get_db)
):
    menu_item = db.query(MenuItem).filter(MenuItem.id == menu_item_id).first()

    if not menu_item:
        raise HTTPException(status_code=404, detail="Menu item not found")

    existing_item = db.query(CartItem).filter(
        CartItem.customer_id == customer_id,
        CartItem.menu_item_id == menu_item_id
    ).first()

    if existing_item:
        existing_item.quantity += quantity
        db.commit()
        db.refresh(existing_item)
        return existing_item

    cart_item = CartItem(
        customer_id=customer_id,
        menu_item_id=menu_item_id,
        quantity=quantity
    )

    db.add(cart_item)
    db.commit()
    db.refresh(cart_item)

    return cart_item


@router.get("/")
def get_cart(customer_id: int, db: Session = Depends(get_db)):
    return db.query(CartItem).filter(CartItem.customer_id == customer_id).all()


@router.delete("/{cart_item_id}")
def remove_cart_item(cart_item_id: int, db: Session = Depends(get_db)):
    cart_item = db.query(CartItem).filter(CartItem.id == cart_item_id).first()

    if not cart_item:
        raise HTTPException(status_code=404, detail="Cart item not found")

    db.delete(cart_item)
    db.commit()

    return {"message": "Cart item removed successfully"}


@router.delete("/clear/{customer_id}")
def clear_cart(customer_id: int, db: Session = Depends(get_db)):
    db.query(CartItem).filter(CartItem.customer_id == customer_id).delete()
    db.commit()

    return {"message": "Cart cleared successfully"}