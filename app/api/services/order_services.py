from sqlalchemy.orm import Session
from app.db.models import Order
from app.api.schemas.order_schemas import OrderCreate, OrderUpdate
from typing import List, Optional
from datetime import datetime
from sqlalchemy import desc


def create_order(db: Session, order_data: OrderCreate) -> Order:
    new_order = Order(
        name=order_data.name,
        email=order_data.email,
        phone=order_data.phone,
        second_phone=order_data.second_phone,
        address=order_data.address,
        state=order_data.state,
        city=order_data.city,
        notes=order_data.notes,
        product=order_data.product,
        color=order_data.color,
        image_url=order_data.image_url,
        size=order_data.size,
        shipping=order_data.shipping,
        total_cost=order_data.total_cost,
        status=order_data.status,
        quantity = order_data.quantity
    )
    db.add(new_order)
    db.commit()
    db.refresh(new_order)
    return new_order


def get_order_by_id(db: Session, order_id: int) -> Optional[Order]:
    return db.query(Order).filter(Order.order_id == order_id).first()


def get_all_orders(db: Session, skip: int = 0, limit: int = 100) -> List[Order]:
    return db.query(Order).order_by(desc(Order.created_at)).offset(skip).limit(limit).all() 

def update_order(db: Session, order_id: int, order_update: OrderUpdate) -> Optional[Order]:
    order = get_order_by_id(db, order_id)
    if not order:
        return None

    for field, value in order_update.dict(exclude_unset=True).items():
        setattr(order, field, value)

    order.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(order)
    return order


def make_read(db : Session, order_id : int):
    order = db.query(Order).filter(Order.order_id == order_id).first()
    if not order:
        return False
    order.is_read = True
    db.commit()
    db.refresh(order)
    return order
    
def delete_order(db: Session, order_id: int) -> bool:
    order = get_order_by_id(db, order_id)
    if not order:
        return False

    db.delete(order)
    db.commit()
    return True
