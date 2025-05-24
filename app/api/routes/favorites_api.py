from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.orm import Session
from typing import List

from app.api.favorite_schemas import FavoriteCreate
from app.api.favorite_services import *
from app.db.database import get_db
from app.api.product_schema_mongo import ProductOut  # Import ProductOut for response model
from app.api.products_services import get_favorite_products_for_user
router = APIRouter(
    prefix="/order-app/api/v1/favorites",
    tags=["favorites"],
)

@router.post("/", response_model=FavoriteCreate)
def add_item_to_favorites(favorite: FavoriteCreate, db: Session = Depends(get_db)):
    """
    إضافة منتج إلى مفضلة المستخدم.

    - يتم الحصول على معرف المستخدم من نص الطلب (user_identifier).
    - يتم الحصول على معرف المنتج من نص الطلب (product_id).
    - يتم استخدام دالة خدمة لإضافة المنتج إلى قاعدة البيانات.
    - إذا تمت الإضافة بنجاح، يتم إرجاع بيانات المفضلة التي تم إنشاؤها.
    - إذا كان المنتج موجودًا بالفعل في المفضلة، يتم إرجاع خطأ 409 (Conflict).
    """
    try:
        db_favorite = add_favorite(db=db, user_identifier=favorite.user_identifier, product_id=favorite.product_id)
        if db_favorite:
            return db_favorite
        else:
            raise HTTPException(status_code=409, detail="المنتج موجود بالفعل في مفضلة المستخدم")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"حدث خطأ أثناء إضافة المنتج إلى المفضلة: {e}")

@router.get("/{user_identifier}", response_model=List[ProductOut])
async def get_user_favorite_products(user_identifier: str, db: Session = Depends(get_db)):
    """
    جلب جميع المنتجات المفضلة لمستخدم معين.

    Args:
        user_identifier: معرف المستخدم (يتم تمريره كجزء من مسار الطلب).
        db: جلسة قاعدة البيانات SQLAlchemy (يتم حقنها باستخدام Depends).

    Returns:
        قائمة بكائنات Favorite تمثل المنتجات المفضلة للمستخدم.
    """
    try:
        favorite_products =await get_favorite_products_for_user(db=db, user_identifier=user_identifier)
        return favorite_products
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"حدث خطأ أثناء جلب المنتجات المفضلة: {e}")
    
@router.post("/clear_one", response_model=bool)
def clear_one_favorite_product(favorite: FavoriteCreate, db: Session = Depends(get_db)):
    """مسح منتج واحد من مفضلة المستخدم."""
    if remove_favorite(db, favorite.user_identifier, favorite.product_id):
        return True
    raise HTTPException(status_code=404, detail="المنتج غير موجود في مفضلة المستخدم")