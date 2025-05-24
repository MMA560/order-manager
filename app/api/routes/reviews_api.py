from fastapi import APIRouter, HTTPException, status, Depends

from sqlalchemy.orm import Session

from typing import List


from app.api.schemas.review_schemas import ReviewCreate, ReviewOut

from app.db.database import get_db

from app.db.models import Review

from app.api.services.review_services import create_new_review, get_reviews_by_product_id


router = APIRouter(

    prefix="/order-app/api/v1/reviews",

    tags=["reviews"],

)


@router.post("/", response_model=ReviewOut, status_code=status.HTTP_201_CREATED)

def create_review(review: ReviewCreate, db: Session = Depends(get_db)):

    try:

        new_review = create_new_review(review_data=review, db=db)

        return new_review

    except Exception as e:

        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Internal sever error {e}")


@router.get("/products/", response_model=List[ReviewOut], status_code=status.HTTP_200_OK)

def get_all_reviews(product_id: int, db: Session = Depends(get_db)):

    return get_reviews_by_product_id(db=db, product_id=product_id)


@router.get("/{review_id}", response_model=ReviewOut, status_code=status.HTTP_200_OK)

def get_review(review_id: int, db: Session = Depends(get_db)):

    review = db.query(Review).filter(Review.review_id == review_id).first()

    if not review:

        raise HTTPException(status_code=404, detail="المراجعة غير موجودة")

    return review


@router.put("/{review_id}", response_model=ReviewOut, status_code=status.HTTP_200_OK)

def update_review(review_id: int, updated_review: ReviewCreate, db: Session = Depends(get_db)):

    review = db.query(Review).filter(Review.review_id == review_id).first()

    if not review:

        raise HTTPException(status_code=404, detail="المراجعة غير موجودة")

    review.reviewer_name = updated_review.reviewer_name

    review.rate = updated_review.rate

    review.comment = updated_review.comment

    db.commit()

    db.refresh(review)

    return review


@router.delete("/{review_id}", status_code=status.HTTP_200_OK)

def delete_review(review_id: int, db: Session = Depends(get_db)):

    review = db.query(Review).filter(Review.review_id == review_id).first()

    if not review:

        raise HTTPException(status_code=404, detail="المراجعة غير موجودة")

    db.delete(review)

    db.commit()

    return {"message": "تم حذف المراجعة بنجاح"}