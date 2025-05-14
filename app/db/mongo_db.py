# db/mongo_db_sync.py
from pymongo import MongoClient
from pymongo.database import Database
from pymongo.collection import Collection
import os # لإدارة سلسلة الاتصال كمتغير بيئة (موصى به)

# استخدم متغير بيئة لسلسلة الاتصال
# تأكد من تعيين متغير بيئة باسم MONGODB_URI في Vercel
MONGO_URI = os.environ.get("MONGODB_URI", "mongodb+srv://mma320:zHcJYVCcKoI5kRYh@cluster0.njoseeb.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")

# قم بتهيئة العميل في المستوى العلوي.
# PyMongo يدير تجميع الاتصالات وإعادة الاتصال تلقائيًا.
try:
    client: MongoClient = MongoClient(MONGO_URI)
    # اختياري: قم بعملية بسيطة للتحقق من الاتصال عند البدء
    client.admin.command('ping')
    print("MongoDB connection successful!")
except Exception as e:
    print(f"Could not connect to MongoDB: {e}")
    # قد تحتاج إلى التعامل مع هذا الخطأ بشكل أفضل في بيئة الإنتاج

# احصل على قاعدة البيانات والـ collection
db: Database = client["my_products"]
products_collection: Collection = db["products"]

# لا تحتاج إلى إغلاق العميل هنا صراحةً؛ دعه مفتوحًا لإعادة استخدامه في الـ Warm Starts