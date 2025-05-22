from sqlalchemy.orm import Session
from app.db import models
from typing import List

def add_favorite(db: Session, user_identifier: str, product_id: int):
    """
    يضيف منتجًا إلى مفضلة المستخدم.

    Args:
        db: جلسة قاعدة البيانات SQLAlchemy.
        user_identifier: معرف المستخدم (من الكوكي).
        product_id: معرف المنتج المراد إضافته إلى المفضلة.

    Returns:
        نموذج Favorite إذا تمت الإضافة بنجاح، وإلا None (إذا كان موجودًا بالفعل).
    """
    existing_favorite = db.query(models.Favorite).filter(
        models.Favorite.user_identifier == user_identifier,
        models.Favorite.product_id == product_id
    ).first()

    if existing_favorite:
        return None  # المنتج موجود بالفعل في المفضلة

    db_favorite = models.Favorite(user_identifier=user_identifier, product_id=product_id)
    db.add(db_favorite)
    db.commit()
    db.refresh(db_favorite)
    return db_favorite

def get_user_favorites(db: Session, user_identifier: str) -> List[models.Favorite]:
    """
    يجلب جميع المنتجات المفضلة لمستخدم معين.

    Args:
        db: جلسة قاعدة البيانات SQLAlchemy.
        user_identifier: معرف المستخدم (من الكوكي).

    Returns:
        قائمة بنماذج Favorite تمثل المنتجات المفضلة للمستخدم.
    """
    return db.query(models.Favorite).filter(
        models.Favorite.user_identifier == user_identifier
    ).all()

def remove_favorite(db: Session, user_identifier: str, product_id: int) -> bool:
    """
    يزيل منتجًا من مفضلة المستخدم.

    Args:
        db: جلسة قاعدة البيانات SQLAlchemy.
        user_identifier: معرف المستخدم (من الكوكي).
        product_id: معرف المنتج المراد إزالته من المفضلة.

    Returns:
        True إذا تمت الإزالة بنجاح، وإلا False (إذا لم يكن المنتج موجودًا في المفضلة).
    """
    favorite_to_delete = db.query(models.Favorite).filter(
        models.Favorite.user_identifier == user_identifier,
        models.Favorite.product_id == product_id
    ).first()

    if favorite_to_delete:
        db.delete(favorite_to_delete)
        db.commit()
        return True
    return False