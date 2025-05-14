from motor.motor_asyncio import AsyncIOMotorClient
from motor.motor_asyncio import AsyncIOMotorDatabase
from motor.motor_asyncio import AsyncIOMotorCollection

client = AsyncIOMotorClient(
    "mongodb+srv://mma320:zHcJYVCcKoI5kRYh@cluster0.njoseeb.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0",
    tls=True,
    tlsAllowInvalidCertificates=True  # في حال كانت الشهادات غير صالحة
)
db = client["my_products"]  # اسم قاعدة البيانات التي تريد استخدامها
products_collection = db["products"]  # الـ Collection لحفظ المنتجات
