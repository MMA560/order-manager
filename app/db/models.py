from sqlalchemy import Column, Integer, String, DateTime, Boolean, Float
from .database import Base
from datetime import datetime


class Order(Base):
    __tablename__ = "orders"
    
    order_id   = Column(Integer, primary_key=True, index=True)
    name       = Column(String(100), index=True)
    email      = Column(String(100), index=True, nullable=True, default=None)
    phone      = Column(String(100), index=True, nullable=False)
    second_phone = Column(String(100), index=True)
    address    = Column(String(500), index=True)
    state      = Column(String(100), index=True)
    city       = Column(String(100), index=True)
    notes      = Column(String(1000))
    created_at = Column(DateTime, index=True, default= datetime.utcnow)
    product    = Column(String(100), index=True)
    color      = Column(String(100), index=True)
    image_url  = Column(String(1000), index=True, nullable=True)
    size       = Column(String(100), index=True)
    quantity   = Column(Integer, default=1, nullable=False)
    shipping   = Column(String(100), index=True)
    total_cost = Column(Float, index=True)
    status = Column(String(50), default="pending")  # أو قيم مثل: pending, confirmed, shipped, delivered
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_read    = Column(Boolean, default=False)


class Review(Base):
    __tablename__ = "reviews"
    
    review_id    = Column(Integer, primary_key=True, index=True)
    reviewer_name = Column(String(100))
    rate         = Column(Integer, nullable=False)
    comment      = Column(String(1000), nullable = False)
    created_at   = Column(DateTime, default=datetime.utcnow)