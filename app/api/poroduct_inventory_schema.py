from pydantic import BaseModel, Field, NonNegativeInt
from typing import Optional

# 1. نموذج أساسي للحقول المشتركة
class ProductInventoryBase(BaseModel):
    product_id: int = Field(..., description="معرف المنتج المرتبط بهذا المخزون.")
    color: str = Field(..., min_length=1, max_length=100, description="اللون المحدد للمنتج.")
    size: str = Field(..., min_length=1, max_length=100, description="المقاس المحدد للمنتج.")
    quantity: NonNegativeInt = Field(0, description="الكمية الحالية للمخزون (يجب أن تكون غير سالبة).")


# 2. نموذج لإنشاء سجل مخزون جديد
# لا يتضمن product_inventory_id لأنه عادةً ما يتم إنشاؤه تلقائيًا بواسطة قاعدة البيانات.
class ProductInventoryCreate(ProductInventoryBase):
    pass # يرث جميع الحقول من ProductInventoryBase

# 3. نموذج لتحديث سجل مخزون موجود
# جميع الحقول هنا اختيارية، حيث قد تحتاج فقط لتحديث الكمية مثلاً.
class ProductInventoryUpdate(BaseModel):
    ordered_quantity: Optional[NonNegativeInt] = Field(None, description="الكمية الجديدة للمخزون (يجب أن تكون غير سالبة).")
    # يمكن إضافة حقول أخرى هنا إذا كنت تسمح بتغييرها بعد الإنشاء.
    # color: Optional[str] = Field(None, min_length=1, max_length=100)
    # size: Optional[str] = Field(None, min_length=1, max_length=100)


# 4. نموذج لتمثيل البيانات بعد استردادها من قاعدة البيانات
# يتضمن product_inventory_id لأنه سيكون موجودًا بعد حفظ السجل.
class ProductInventoryOut(ProductInventoryBase):
    product_inventory_id: int = Field(..., description="المعرف الفريد لبند المخزون في قاعدة البيانات.")

    class Config:
        from_attributes = True # هذا يسمح لـ Pydantic بقراءة البيانات مباشرة من نماذج SQLAlchemy
        # orm_mode = True is deprecated in Pydantic v2. Instead, use from_attributes = True
        # from_attributes = True # For Pydantic v2+