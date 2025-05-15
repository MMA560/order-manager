import os
from google.cloud import firestore  # استيراد firestore بشكل صحيح
from dotenv import load_dotenv

# تحميل متغيرات البيئة من ملف .env
load_dotenv()

# تأكد من أن متغير GOOGLE_APPLICATION_CREDENTIALS مضبوط بشكل صحيح
credentials_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
if not credentials_path:
    raise Exception("GOOGLE_APPLICATION_CREDENTIALS not set!")

# تأكد من أن البيئة تتعرف على الاعتماديات
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = credentials_path

# تهيئة العميل للاتصال بـ Firestore
db = firestore.AsyncClient()  # استخدام AsyncClient لتشغيل العمليات غير المتزامنة
products_collection = db.collection("products")  # تحديد الـ collection الخاص بالمنتجات
