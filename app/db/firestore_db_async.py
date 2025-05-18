import os
import json # نحتاج لاستيراد مكتبة json
from google.cloud import firestore
from dotenv import load_dotenv
import google.oauth2.service_account # نحتاج لهذه المكتبة لإنشاء كائن الاعتماد

# تحميل متغيرات البيئة من ملف .env (محلياً)
load_dotenv()

# === بداية التعديل ===

# اسم متغير البيئة الذي يحتوي على محتوى JSON لمفتاح حساب الخدمة على Vercel
# تأكد أن هذا هو نفس الاسم الذي استخدمته على Vercel
CREDENTIALS_JSON_ENV_VAR = "FIREBASE_SERVICE_ACCOUNT_JSON" # مثال لاسم متغير جديد

# قراءة محتوى JSON من متغير البيئة الجديد
credentials_json_string = os.getenv(CREDENTIALS_JSON_ENV_VAR)

if not credentials_json_string:
    # إذا لم يتم العثور على متغير البيئة الجديد، قد يكون هناك fallback
    # مثلاً، إذا كنت لا تزال تستخدم GOOGLE_APPLICATION_CREDENTIALS كمسار ملف محلياً
    # أو يمكنك رفع خطأ إذا كان هذا المتغير إلزاميًا في بيئة Vercel
    # هنا نفترض أنه إلزامي على Vercel
    raise ValueError(f"Environment variable {CREDENTIALS_JSON_ENV_VAR} not set or is empty.")

# تحليل (parse) سلسلة JSON إلى قاموس Python
try:
    credentials_info = json.loads(credentials_json_string)
except json.JSONDecodeError as e:
    raise ValueError(f"Failed to decode JSON from {CREDENTIALS_JSON_ENV_VAR}: {e}") from e

# استخراج project_id من معلومات الاعتماد (لأنه مطلوب عند تهيئة العميل أحياناً)
project_id = credentials_info.get('project_id')
if not project_id:
    raise ValueError("Project ID not found in credentials JSON.")


# إنشاء كائن بيانات الاعتماد من القاموس
try:
    credentials = google.oauth2.service_account.Credentials.from_service_account_info(credentials_info)
except Exception as e:
    raise RuntimeError(f"Failed to create credentials from JSON info: {e}") from e


# === نهاية التعديل ===

# تهيئة العميل للاتصال بـ Firestore باستخدام بيانات الاعتماد التي تم تحميلها
# مرر كائن الاعتماديات و project_id بشكل صريح
db = firestore.AsyncClient(credentials=credentials, project=project_id)

# تحديد الـ collection الخاص بالمنتجات
products_collection = db.collection("products")

print("Firestore client initialized successfully.")

# يمكنك الآن البدء في استخدام products_collection لإجراء عمليات على قاعدة البيانات
# مثال (تحتاج إلى تشغيله داخل دالة async):
# async def get_products():
#     docs = products_collection.stream()
#     async for doc in docs:
#         print(f"{doc.id} => {doc.to_dict()}")