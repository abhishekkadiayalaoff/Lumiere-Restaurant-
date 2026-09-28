from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.menu_item import MenuItem
from app.models.user import User, UserRole
from app.api.dependencies import require_roles

router = APIRouter()


@router.post("/")
def create_menu_item(
    name: str,
    category: str,
    price: float,
    description: str = "",
    image_url: str = "",
    db: Session = Depends(get_db)
):
    item = MenuItem(
        name=name,
        category=category,
        price=price,
        description=description,
        image_url=image_url
    )

    db.add(item)
    db.commit()
    db.refresh(item)

    return item


@router.get("/")
def get_menu_items(db: Session = Depends(get_db)):
    return db.query(MenuItem).all()


@router.get("/{item_id}")
def get_menu_item(item_id: int, db: Session = Depends(get_db)):
    item = db.query(MenuItem).filter(MenuItem.id == item_id).first()

    if not item:
        raise HTTPException(status_code=404, detail="Menu item not found")

    return item


@router.put("/{item_id}")
def update_menu_item(
    item_id: int,
    name: str,
    category: str,
    price: float,
    description: str = "",
    image_url: str = "",
    is_available: bool = True,
    db: Session = Depends(get_db)
):
    item = db.query(MenuItem).filter(MenuItem.id == item_id).first()

    if not item:
        raise HTTPException(status_code=404, detail="Menu item not found")

    item.name = name
    item.category = category
    item.price = price
    item.description = description
    item.image_url = image_url
    item.is_available = is_available

    db.commit()
    db.refresh(item)

    return item


@router.delete("/{item_id}")
def delete_menu_item(item_id: int, db: Session = Depends(get_db)):
    item = db.query(MenuItem).filter(MenuItem.id == item_id).first()

    if not item:
        raise HTTPException(status_code=404, detail="Menu item not found")

    db.delete(item)
    db.commit()

    return {"message": "Menu item deleted successfully"}


@router.patch("/{item_id}/availability")
def update_menu_item_availability(
    item_id: int,
    is_available: bool,
    db: Session = Depends(get_db)
):
    item = db.query(MenuItem).filter(MenuItem.id == item_id).first()

    if not item:
        raise HTTPException(status_code=404, detail="Menu item not found")

    item.is_available = is_available
    db.commit()
    db.refresh(item)

    return {
        "message": "Menu item availability updated",
        "item_id": item.id,
        "is_available": item.is_available
    }