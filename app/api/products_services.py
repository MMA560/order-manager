# api/products_services_sync.py
# استيراد الـ collection المتزامنة
from app.db.mongo_db import products_collection
# استيراد الـ Schema الخاص بك
from app.api.product_schema_mongo import Product
from typing import List

# الدوال أصبحت متزامنة (لا يوجد async أو await بداخلها لعمليات DB)

def get_all_products_sync() -> List[Product]:
    # .find() هنا يرجع cursor متزامن، نستخدم list() لتحويله
    products = list(products_collection.find().limit(1000))
    result_list = []
    for product_dict in products:
        # تأكد من التعامل مع _id إذا كان موجودًا ولا تريده في الـ response
        # أو قم بتحويل ObjectId إلى str إذا كان الـ Schema يتوقعه كذلك
        # بما أنك تستخدم 'id' رقمي في الاستعلامات، سأفترض أن _id يتم تجاهله هنا
        product_dict.pop("_id", None)
        result_list.append(Product(**product_dict))
    return result_list

def get_product_by_id_sync(product_id: int) -> Product | None:
    # find_one() هنا عملية متزامنة وتحظر حتى يتم جلب النتيجة
    product_dict = products_collection.find_one({"id": product_id})
    if product_dict:
        product_dict.pop("_id", None)
        return Product(**product_dict)
    return None # إرجاع None إذا لم يتم العثور على المنتج

def add_product_sync(product: Product) -> Product:
    # insert_one() هنا عملية متزامنة
    product_dict = product.dict()
    # إذا كنت تستخدم id رقمي خاص بك، تأكد من وجوده في product_dict قبل الإدخال
    # لا تستخدم result.inserted_id لتعيين الـ id الرقمي، لأنه ObjectId
    result = products_collection.insert_one(product_dict)
    # يمكنك إرجاع الـ product الذي تم إدخاله كما هو، أو جلبه مرة أخرى إذا احتجت لـ _id
    # بما أن الـ schema هو Product الذي يتوقع id رقمي، سنرجع الـ dict الأصلي
    return Product(**product_dict)


def update_product_sync(product_id: int, product: Product) -> Product | None:
    product_dict = product.dict(exclude_unset=True)
    # update_one() عملية متزامنة
    result = products_collection.update_one({"id": product_id}, {"$set": product_dict})
    if result.matched_count:
        # إذا تم التحديث، نرجع البيانات المحدثة (يمكنك جلبها مرة أخرى للتأكد التام)
        # بما أنك تقوم بإرجاع Product(**product_dict)، هذا يعني أن الـ dict يحتوي على التحديثات
        return Product(**product_dict)
    return None # إرجاع None إذا لم يتم العثور على المستند للمطابقة

def delete_product_sync(product_id: int) -> bool:
    # delete_one() عملية متزامنة
    result = products_collection.delete_one({"id": product_id})
    return result.deleted_count > 0