from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class ReviewCreate(BaseModel):
    
    reviewer_name : Optional[str] = None
    rate : int
    comment : str
    product_id : int
    
class ReviewOut(ReviewCreate):
    review_id : int
    created_at : datetime
    product_id : int