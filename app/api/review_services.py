from sqlalchemy.orm import Session
from app.db.models import Review
from app.api.review_schemas import ReviewCreate, ReviewOut
from typing import Optional


def create_new_review(db: Session, review_data: ReviewCreate) -> Review:
    review = Review(
        reviewer_name=review_data.reviewer_name,
        rate=review_data.rate,
        comment=review_data.comment,
        product_id = review_data.product_id
    )
    db.add(review)
    db.commit()
    db.refresh(review)
    return review


def get_review(db: Session, review_id: int) -> Review:
    return db.query(Review).filter(Review.review_id == review_id).first()


def get_reviews_by_product_id(db: Session, product_id : int) -> list[Review]:
    return db.query(Review).filter(Review.product_id == product_id).all()


def update_review(db: Session, review_id: int, updated_data: ReviewCreate) -> Optional[Review]:
    review = db.query(Review).filter(Review.review_id == review_id).first()
    if review:
        review.reviewer_name= updated_data.reviewer_name
        review.rate = updated_data.rate
        review.comment = updated_data.comment
        db.commit()
        db.refresh(review)
    return review


def delete_review(db: Session, review_id: int) -> bool:
    review = db.query(Review).filter(Review.review_id == review_id).first()
    if review:
        db.delete(review)
        db.commit()
        return True
    return False
