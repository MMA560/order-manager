from app.db.mongo_db import products_collection
from app.api.product_schema_mongo import Product


async def get_all_products():
    products = await products_collection.find().to_list(1000)
    for product in products:
        product.pop("_id", None)
    return [Product(**product) for product in products]


async def get_product_by_id(product_id: int):
    product = await products_collection.find_one({"id": product_id})
    if product:
        product.pop("_id", None)
        return Product(**product)
    return None


async def add_product(product: Product):
    result = await products_collection.insert_one(product.dict())
    # إرجاع المنتج مع الـ id الجديد
    product_dict = product.dict()
    product_dict["id"] = result.inserted_id  # استبدال الـ id بالقيمة من الـ db
    return Product(**product_dict)


async def update_product(product_id: int, product: Product):
    product_dict = product.dict(exclude_unset=True)  # إتاحة التحديث فقط للحقول المعدلة
    result = await products_collection.update_one({"id": product_id}, {"$set": product_dict})
    if result.matched_count:
        return Product(**product_dict)  # إرجاع المنتج مع التحديثات
    return None


async def delete_product(product_id: int):
    result = await products_collection.delete_one({"id": product_id})
    return result.deleted_count > 0  # إرجاع True إذا تم الحذف
