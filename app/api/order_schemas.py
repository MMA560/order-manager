from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime


class OrderBase(BaseModel):
    name: str
    email: Optional[EmailStr] = None
    phone: str
    second_phone: Optional[str] = None
    address: str
    state: str
    city: str
    notes: Optional[str] = None
    product: str
    color: Optional[str] = None
    image_url: Optional[str] = None
    size: Optional[str] = None
    shipping: Optional[float] = None
    total_cost: float
    status : str = "Pending"


class OrderCreate(OrderBase):
    pass


class OrderUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    second_phone: Optional[str] = None
    address: Optional[str] = None
    state: Optional[str] = None
    city: Optional[str] = None
    notes: Optional[str] = None
    product: Optional[str] = None
    color: Optional[str] = None
    image_url: Optional[str] = None
    size: Optional[str] = None
    shipping: Optional[str] = None
    total_cost: Optional[float] = None
    status: Optional[str] = None
    
    class config:
        from_attributes = True


class OrderOut(OrderBase):
    order_id: int
    status: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
