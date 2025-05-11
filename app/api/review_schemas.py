from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class ReviewCreate(BaseModel):
    
    reviewer_name : Optional[str] = None
    rate : int
    comment : str
    
class ReviewOut(ReviewCreate):
    review_id : int
    created_at: datetime