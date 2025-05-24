from fastapi import APIRouter, HTTPException, status, Depends, Path, Body
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import List
import logging

from app.db.database import get_db
from app.db.models import ProductInventory
from app.api.poroduct_inventory_schema import ProductInventoryCreate, ProductInventoryOut, ProductInventoryUpdate

router = APIRouter(
    prefix="/order-app/api/v1/inventory",
    tags=["inventory"],
)

logger = logging.getLogger(__name__)

@router.post("/", response_model=ProductInventoryOut, status_code=status.HTTP_201_CREATED,
             summary="إنشاء بند مخزون جديد",
             description="يضيف بند مخزون جديد لتركيبة منتج ولون ومقاس محددة. يجب أن تكون تركيبة المنتج واللون والمقاس فريدة.")
def create_inventory_item(
    inventory_item: ProductInventoryCreate,
    db: Session = Depends(get_db)
):
    try:
        db_item = ProductInventory(**inventory_item.dict())
        db.add(db_item)
        db.commit()
        db.refresh(db_item)
        logger.info(f"تم إنشاء بند مخزون جديد: {db_item.product_inventory_id}")
        return db_item
    except IntegrityError as e:
        db.rollback()
        if "unique constraint" in str(e).lower():
            logger.warning(f"محاولة إنشاء بند مخزون مكرر: Product ID {inventory_item.product_id}, Color {inventory_item.color}, Size {inventory_item.size}")
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"بند المخزون لهذه التركيبة (المنتج, اللون, المقاس) موجود بالفعل. استخدم نقطة التحديث لتغيير الكمية."
            )
        else:
            logger.error(f"خطأ في قاعدة البيانات عند إنشاء بند مخزون: {e}", exc_info=True)
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="خطأ في قاعدة البيانات")
    except Exception as e:
        logger.error(f"خطأ غير متوقع عند إنشاء بند مخزون: {e}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"خطأ داخلي في الخادم: {e}")

@router.get("/{item_id}", response_model=ProductInventoryOut, status_code=status.HTTP_200_OK,
            summary="جلب بند مخزون بواسطة المعرف",
            description="يسترد تفاصيل بند مخزون محدد باستخدام معرفه الفريد.")
def get_inventory_item_by_id(
    item_id: int = Path(..., description="معرف بند المخزون الفريد"),
    db: Session = Depends(get_db)
):
    db_item = db.query(ProductInventory).filter(ProductInventory.product_inventory_id == item_id).first()
    if db_item is None:
        logger.warning(f"طلب بند مخزون غير موجود: ID {item_id}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="بند المخزون غير موجود")
    return db_item

@router.get("/products/{product_id}", response_model=List[ProductInventoryOut], status_code=status.HTTP_200_OK,
            summary="جلب كل بنود المخزون لمنتج معين",
            description="يسترد قائمة بكل بنود المخزون (ألوان ومقاسات مختلفة) لمنتج معين باستخدام معرف المنتج.")
def get_inventory_by_product_id(
    product_id: int = Path(..., description="معرف المنتج الذي ترغب في جلب بنود المخزون الخاصة به"),
    db: Session = Depends(get_db)
):
    items = db.query(ProductInventory).filter(ProductInventory.product_id == product_id).all()
    if not items:
        logger.info(f"لا يوجد مخزون للمنتج ID: {product_id}")
        return []
    return items

@router.patch("/{item_id}", response_model=ProductInventoryOut, status_code=status.HTTP_200_OK,
             summary="تحديث الكمية في بند مخزون",
             description="يقوم بتحديث الكمية المتاحة لبند مخزون معين.")
def update_inventory_quantity(
    item_id: int = Path(..., description="معرف بند المخزون الفريد المراد تحديثه"),
    inventory_update: ProductInventoryUpdate = Body(..., description="بيانات التحديث (الكمية الجديدة)."),
    db: Session = Depends(get_db)
):
    db_item = db.query(ProductInventory).filter(ProductInventory.product_inventory_id == item_id).first()
    if db_item is None:
        logger.warning(f"محاولة تحديث بند مخزون غير موجود: ID {item_id}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="بند المخزون غير موجود")

    if inventory_update.ordered_quantity is not None:
        if db_item.quantity - inventory_update.ordered_quantity < 0:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="الكمية المطلوبة أكبر من الكمية المتاحة.")
        db_item.quantity -= inventory_update.ordered_quantity

    try:
        db.commit()
        db.refresh(db_item)
        logger.info(f"تم تحديث الكمية لبند المخزون {item_id} إلى {db_item.quantity}")
        return db_item
    except Exception as e:
        db.rollback()
        logger.error(f"خطأ عند تحديث بند المخزون {item_id}: {e}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"خطأ في قاعدة البيانات: {e}")

@router.delete("/{item_id}", status_code=status.HTTP_200_OK,
             summary="حذف بند مخزون",
             description="يقوم بحذف بند مخزون محدد من قاعدة البيانات.")
def delete_inventory_item(
    item_id: int = Path(..., description="معرف بند المخزون الفريد المراد حذفه"),
    db: Session = Depends(get_db)
):
    db_item = db.query(ProductInventory).filter(ProductInventory.product_inventory_id == item_id).first()
    if db_item is None:
        logger.warning(f"محاولة حذف بند مخزون غير موجود: ID {item_id}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="بند المخزون غير موجود")

    try:
        db.delete(db_item)
        db.commit()
        logger.info(f"تم حذف بند المخزون: {item_id}")
        return {"message": "تم حذف بند المخزون بنجاح"}
    except Exception as e:
        db.rollback()
        logger.error(f"خطأ عند حذف بند المخزون {item_id}: {e}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"خطأ في قاعدة البيانات: {e}")