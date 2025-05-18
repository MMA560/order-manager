import os
import json # نحتاج لاستيراد مكتبة json
from google.cloud import firestore
from dotenv import load_dotenv
import google.oauth2.service_account # نحتاج لهذه المكتبة لإنشاء كائن الاعتماد

# استيراد FieldFilter لإصلاح التحذير
from google.cloud.firestore_v1.base_query import FieldFilter

# تحميل متغيرات البيئة من ملف .env (محلياً)
load_dotenv()

# === هذا الجزء هو نفس الجزء الذي تحدثنا عنه لتهيئة العميل ===
# تأكد من أن هذا الجزء موجود وصحيح في ملف firestore_db_async.py
# اسم متغير البيئة الذي يحتوي على محتوى JSON لمفتاح حساب الخدمة
CREDENTIALS_JSON_ENV_VAR = "GCP_FIREBASE_CREDENTIALS_JSON" # استخدم نفس الاسم الذي وضعته في .env أو على Vercel

# قراءة محتوى JSON من متغير البيئة الجديد
credentials_json_string = os.getenv(CREDENTIALS_JSON_ENV_VAR)

if not credentials_json_string:
    raise ValueError(f"Environment variable {CREDENTIALS_JSON_ENV_VAR} not set or is empty. Cannot load credentials.")

# تحليل سلسلة JSON
try:
    credentials_info = json.loads(credentials_json_string)
except json.JSONDecodeError as e:
    raise ValueError(f"Failed to decode JSON from {CREDENTIALS_JSON_ENV_VAR}: {e}") from e

# استخراج project_id
project_id = credentials_info.get('project_id')
if not project_id:
    raise ValueError("Project ID not found in credentials JSON.")

# إنشاء كائن بيانات الاعتماد
try:
    credentials = google.oauth2.service_account.Credentials.from_service_account_info(credentials_info)
except Exception as e:
    raise RuntimeError(f"Failed to create credentials from JSON info: {e}") from e

# تهيئة العميل وتمرير الاعتماديات ومعرف المشروع بشكل صريح
db = firestore.AsyncClient(credentials=credentials, project=project_id)

# تحديد الـ collection الخاص بالمنتجات
products_collection = db.collection("products")

print("Firestore client initialized successfully.")
# === نهاية جزء تهيئة العميل ===


# ============================================================
# هذا هو الكود الذي قمت بتوفيره مع التحديثات لإزالة التحذير
# ============================================================

# تأكد أن هذه الاستيرادات صحيحة وموجودة في ملف products_services.py
# من app.db.firestore_db_async import products_collection # تم استيرادها بالفعل أعلاه في نفس الملف في هذا المثال
from app.api.product_schema_mongo import Product # تأكد من وجود هذا الملف والكلاس
from typing import List, Optional

# Get all products
async def get_all_products() -> List[Product]:
    # هذا الجزء لا يستخدم where() فلا يحتاج تعديل
    docs = products_collection.stream()
    result = []
    async for doc in docs:
        data = doc.to_dict()
        result.append(Product(**data))
    return result

# Get product by ID
async def get_product_by_id(product_id: int) -> Optional[Product]:
    # === التحديث هنا لاستخدام filter=FieldFilter ===
    query = products_collection.where(filter=FieldFilter("id", "==", product_id)).limit(1)
    # =============================================
    docs = query.stream()
    async for doc in docs:
        return Product(**doc.to_dict())
    return None

# Add product
async def add_product(product: Product) -> Product:
    # هذا الجزء لا يستخدم where() فلا يحتاج تعديل
    product_dict = product.dict()
    await products_collection.add(product_dict) # ملاحظة: add ينشئ document ID تلقائي، إذا كنت تحتاج id محدد، استخدم .document(id).set(data)
    return product

# Update product by ID
async def update_product(product_id: int, product: Product) -> Optional[Product]:
    # === التحديث هنا لاستخدام filter=FieldFilter ===
    query = products_collection.where(filter=FieldFilter("id", "==", product_id)).limit(1)
    # =============================================
    docs = query.stream()
    async for doc in docs:
        # استخدم product.model_dump(exclude_unset=True) إذا كنت تستخدم Pydantic V2+
        await doc.reference.update(product.dict(exclude_unset=True))
        updated_data = await doc.reference.get()
        return Product(**updated_data.to_dict())
    return None

# Delete product by ID
async def delete_product(product_id: int) -> bool:
    # === التحديث هنا لاستخدام filter=FieldFilter ===
    query = products_collection.where(filter=FieldFilter("id", "==", product_id)).limit(1)
    # =============================================
    docs = query.stream()
    async for doc in docs:
        await doc.reference.delete()
        return True
    return False

# يمكنك الآن استخدام هذه الدوال في نقاط النهاية (API endpoints) الخاصة بك.