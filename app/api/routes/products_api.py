from fastapi import APIRouter, HTTPException, status
from typing import List

from app.api.product_schema_mongo import Product, ProductOut
from app.api.products_services import get_all_products, get_product_by_id, add_product, update_product, delete_product

router = APIRouter(
    prefix="/order-app/api/v1/products",
    tags=["products"],
)

@router.get("/", response_model=List[ProductOut], status_code=status.HTTP_200_OK,
         summary="جلب كل المنتجات",
         description="يسترد قائمة بكل المنتجات في قاعدة البيانات.")
async def get_all_products_from_db():
    try:
        return await get_all_products()
    except Exception as e:
        error_detail = f"حدث خطأ أثناء جلب جميع المنتجات من قاعدة البيانات: {str(e)}"
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=error_detail)

@router.get("/{product_id}", response_model=Product, status_code=status.HTTP_200_OK,
            summary="جلب منتج بواسطة المعرف",
            description="يسترد تفاصيل منتج محدد باستخدام معرفه الفريد.")
async def get_product_by_id_from_db(product_id: int):
    try:
        product = await get_product_by_id(product_id)
        if product:
            return product
        else:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"المنتج ذو المعرف {product_id} غير موجود.")
    except Exception as e:
        error_detail = f"حدث خطأ أثناء جلب المنتج ذو المعرف {product_id} من قاعدة البيانات: {str(e)}"
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=error_detail)

@router.post("/", response_model=Product, status_code=status.HTTP_201_CREATED,
             summary="إنشاء منتج جديد",
             description="يضيف منتج جديد إلى قاعدة البيانات.")
async def create_product_in_db(product: Product):
    try:
        return await add_product(product)
    except Exception as e:
        error_detail = f"حدث خطأ أثناء إنشاء منتج جديد في قاعدة البيانات: {str(e)}"
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=error_detail)

@router.put("/{product_id}", response_model=Product, status_code=status.HTTP_200_OK,
            summary="تحديث منتج",
            description="يقوم بتحديث تفاصيل منتج محدد باستخدام معرفه الفريد.")
async def update_product_in_db(product_id: int, product: Product):
    try:
        updated_product = await update_product(product_id, product)
        if updated_product:
            return updated_product
        else:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"المنتج ذو المعرف {product_id} غير موجود أو لم يتم تحديثه.")
    except Exception as e:
        error_detail = f"حدث خطأ أثناء تحديث المنتج ذو المعرف {product_id} في قاعدة البيانات: {str(e)}"
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=error_detail)

@router.delete("/{product_id}", status_code=status.HTTP_200_OK,
             summary="حذف منتج",
             description="يقوم بحذف منتج محدد من قاعدة البيانات.")
async def delete_product_in_db(product_id: int):
    try:
        deleted = await delete_product(product_id)
        if deleted:
            return {"detail": f"تم حذف المنتج ذو المعرف {product_id} بنجاح."}
        else:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"المنتج ذو المعرف {product_id} غير موجود.")
    except Exception as e:
        error_detail = f"حدث خطأ أثناء حذف المنتج ذو المعرف {product_id} من قاعدة البيانات: {str(e)}"
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=error_detail)