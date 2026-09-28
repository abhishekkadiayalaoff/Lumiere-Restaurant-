from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.table import RestaurantTable, TableStatus

router = APIRouter()


@router.post("/")
def create_table(
    table_number: str,
    capacity: int = 2,
    db: Session = Depends(get_db)
):
    existing_table = db.query(RestaurantTable).filter(
        RestaurantTable.table_number == table_number
    ).first()

    if existing_table:
        raise HTTPException(status_code=400, detail="Table already exists")

    table = RestaurantTable(
        table_number=table_number,
        capacity=capacity,
        status=TableStatus.available
    )

    db.add(table)
    db.commit()
    db.refresh(table)

    return table


@router.get("/")
def get_tables(db: Session = Depends(get_db)):
    return db.query(RestaurantTable).all()


@router.patch("/{table_id}/status")
def update_table_status(
    table_id: int,
    status: TableStatus,
    db: Session = Depends(get_db)
):
    table = db.query(RestaurantTable).filter(
        RestaurantTable.id == table_id
    ).first()

    if not table:
        raise HTTPException(status_code=404, detail="Table not found")

    table.status = status
    db.commit()
    db.refresh(table)

    return table


@router.delete("/{table_id}")
def delete_table(table_id: int, db: Session = Depends(get_db)):
    table = db.query(RestaurantTable).filter(
        RestaurantTable.id == table_id
    ).first()

    if not table:
        raise HTTPException(status_code=404, detail="Table not found")

    db.delete(table)
    db.commit()

    return {"message": "Table deleted successfully"}