from fastapi import FastAPI, status
from fastapi.middleware.cors import CORSMiddleware

from app.db.database import Base, enigne
from app.api.routes import orders_api, favorites_api, inventory_api, reviews_api, products_api
import logging

# إعداد بسيط لـ logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# تهيئة قاعدة البيانات
Base.metadata.create_all(bind=enigne)

app = FastAPI(
    title="نظام إدارة الطلبات والمخزون",
    description="API لحفظ الطلبات وإرسال تفاصيلها عبر البريد الإلكتروني وإدارة مخزون المنتجات.",
    version="1.0.0",
    contact={
        "name": "محمد مجاهد",
        "email": "mohamadmegahed320@gmail.com",
    },
    license_info={
        "name": "MIT",
        "url": "https://opensource.org/licenses/MIT",
    }
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/", status_code=status.HTTP_200_OK)
def root():
    return {"msg": "Welcome to Order and Inventory Management App"}

# تضمين الراوتر
app.include_router(orders_api.router)
app.include_router(reviews_api.router)
app.include_router(inventory_api.router)
app.include_router(products_api.router)
app.include_router(favorites_api.router)