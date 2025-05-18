# app/db/firestore_db_async.py

import os
import json
from google.cloud import firestore
from dotenv import load_dotenv
import google.oauth2.service_account
# يمكن استيراد FieldFilter هنا أيضاً إذا كنت ستستخدمه في استعلامات مباشرة هنا
# from google.cloud.firestore_v1.base_query import FieldFilter


# تحميل متغيرات البيئة من ملف .env عند استيراد هذا الملف
# يجب أن يكون ملف .env في المجلد الحالي أو مجلد أب
load_dotenv()

# اسم متغير البيئة الذي يحتوي على محتوى JSON لمفتاح حساب الخدمة
# === استخدم نفس الاسم الذي وضعته في ملف .env وعلى Vercel ===
CREDENTIALS_JSON_ENV_VAR = "GCP_FIREBASE_CREDENTIALS_JSON" # مثال: تأكد من مطابقة الاسم في الملفين

# قراءة محتوى JSON من متغير البيئة
credentials_json_string = os.getenv(CREDENTIALS_JSON_ENV_VAR)

# تحقق من أن المتغير موجود وقيمته غير فارغة
if not credentials_json_string:
    # إذا لم يتم العثور على المتغير، ارفع خطأ واضحاً
    # هذا الخطأ يعني أن ملف .env لم يتم تحميله بشكل صحيح أو أن المتغير غير موجود فيه/فارغ
    raise ValueError(
        f"Environment variable {CREDENTIALS_JSON_ENV_VAR} not set or is empty. "
        "Please ensure your .env file is correct and located in the project root, "
        "or that the environment variable is set on your hosting platform."
    )

# تحليل سلسلة JSON إلى قاموس Python
try:
    credentials_info = json.loads(credentials_json_string)
except json.JSONDecodeError as e:
    raise ValueError(
        f"Failed to decode JSON from environment variable {CREDENTIALS_JSON_ENV_VAR}. "
        "Please check the JSON content in your .env file or environment variable settings for errors."
    ) from e

# استخراج project_id من معلومات الاعتماد
project_id = credentials_info.get('project_id')
if not project_id:
    raise ValueError(
        f"Project ID not found in credentials JSON loaded from {CREDENTIALS_JSON_ENV_VAR}. "
        "Please ensure the 'project_id' field exists and is correct in your credentials JSON."
    )

# إنشاء كائن بيانات الاعتماد من القاموس
try:
    credentials = google.oauth2.service_account.Credentials.from_service_account_info(credentials_info)
except Exception as e:
    raise RuntimeError(
        f"Failed to create Google Cloud credentials from the provided JSON info loaded from {CREDENTIALS_JSON_ENV_VAR}. "
        "Please check the 'private_key' field and ensure the entire JSON content is correct and not truncated."
    ) from e

# تهيئة العميل للاتصال بـ Firestore باستخدام بيانات الاعتماد التي تم تحميلها
# مرر كائن الاعتماديات و project_id بشكل صريح
db = firestore.AsyncClient(credentials=credentials, project=project_id)

# تحديد الـ collection الخاص بالمنتجات (يمكن تعريف collections أخرى هنا أيضاً)
products_collection = db.collection("products")

print("Firestore client initialized successfully.")

# ملاحظة: يمكنك الآن استيراد 'db' أو 'products_collection' من هذا الملف
# في ملفات أخرى في مشروعك (مثل app/api/products_services.py)
# مثال: from app.db.firestore_db_async import db, products_collection