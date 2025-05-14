from fastapi import FastAPI, HTTPException, status, Depends, Path, Body
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError # To handle UniqueConstraint errors
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib
from datetime import datetime
from typing import List, Optional # Import List for type hints

# استيرادات الوحدات المحلية الخاصة بك
from app.api.tempelate import *
from app.api.order_schemas import *
# Corrected typo: enigne to engine
from app.db.database import *
from app.api.order_services import *

# NEW IMPORTS FOR INVENTORY
from app.db.models import ProductInventory # Assuming ProductInventory model is here
# NEW IMPORTS FOR PRODUCTS
from app.api.products_services import *
from app.api.product_schema_mongo import *

import logging

# إعداد بسيط لـ logging
# في تطبيق حقيقي، يجب أن يكون لديك إعداد logging أكثر تعقيدًا في ملف منفصل
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# تهيئة قاعدة البيانات
Base.metadata.create_all(bind=enigne) # Corrected typo: enigne to engine

app = FastAPI(
    title="نظام إدارة الطلبات والمخزون", # Updated title
    description="API لحفظ الطلبات وإرسال تفاصيلها عبر البريد الإلكتروني وإدارة مخزون المنتجات.", # Updated description
    version="1.0.0",
    contact={
        "name": "محمد مجاهد",
        "email": "mohamadmegahed320@gmail.com",
        "url": "https://your-website.com",
    },
    license_info={
        "name": "MIT",
        "url": "https://opensource.org/licenses/MIT",
    }
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # السماح لكل النطاقات، يمكن تحديد نطاقات معينة هنا مثل ['http://localhost:3000']
    allow_credentials=True,
    allow_methods=["*"],  # السماح بكل طرق HTTP مثل GET و POST
    allow_headers=["*"],  # السماح بكل الرؤوس
)


# إعدادات الإيميل (استخدم .env في التطبيق الحقيقي لتأمين بيانات الاعتماد)
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
EMAIL_ADDRESS = "zxz01144@gmail.com"
EMAIL_PASSWORD = "ikbw fgvp xmno fvlg"

@app.get("/", status_code=status.HTTP_200_OK)
def root():
    return {"msg":"Welcome to Order and Inventory Management App"} # Updated message

@app.post("/order-app/api/v1/create-order/", status_code=status.HTTP_200_OK)
def create_order_endpoint(order_data: OrderCreate, to_email : str, db: Session = Depends(get_db)):
    # ملاحظة: أخطاء التحقق من صحة Pydantic (التي تسبب 422) تحدث قبل وصول الطلب إلى هنا.
    # FastAPI يتعامل معها تلقائيًا ويسجلها في الكونسول الخاص بالخادم.

    # حفظ الطلب في قاعدة البيانات
    order = create_order(db=db, order_data=order_data)

    # تحضير محتوى الإيميل
    html_content = generate_order_email_html(order_data)
    msg = MIMEMultipart("alternative")
    msg["Subject"] = f"تأكيد طلب {order_data.name}!- {format_datetime_arabic()}"
    msg["From"] = "Rush Kicks"
    msg["To"] = to_email
    msg.attach(MIMEText("تم استلام طلبك بنجاح. التفاصيل موجودة بالأسفل.", "plain"))
    msg.attach(MIMEText(html_content, "html"))

    # إرسال الإيميل
    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            server.send_message(msg)
    except Exception as e:
        # <--- تم إضافة هذا السطر لتسجيل الخطأ في الكونسول الخاص بالـ backend
        logger.error(f"فشل إرسال البريد الإلكتروني للطلب (ID: {order.order_id if order else 'غير متوفر'}): {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"تم حفظ الطلب ولكن فشل إرسال الإيميل: {str(e)}")

    return {"message": "تم إنشاء الطلب وإرسال الإيميل بنجاح"}


@app.get("/order-app/api/v1/orders/{order_id}", status_code=status.HTTP_200_OK)
def get_order(order_id: int = Path(..., description="رقم الطلب"), db: Session = Depends(get_db)):
    order = get_order_by_id(db, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="الطلب غير موجود")
    return order

# جلب كل الطلبات مع إمكانية التصفح (Pagination)
@app.get("/order-app/api/v1/orders/", status_code=status.HTTP_200_OK)
def get_orders(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return get_all_orders(db, skip=skip, limit=limit)

# تحديث طلب
@app.put("/order-app/api/v1/orders/{order_id}", status_code=status.HTTP_200_OK)
def update_order_endpoint(
    order_id: int,
    order_update: OrderUpdate = Body(...),
    db: Session = Depends(get_db)
):
    updated_order = update_order(db, order_id, order_update)
    if not updated_order:
        raise HTTPException(status_code=404, detail="الطلب غير موجود")
    return updated_order

# حذف طلب
@app.delete("/order-app/api/v1/orders/{order_id}", status_code=status.HTTP_200_OK)
def delete_order_endpoint(order_id: int, db: Session = Depends(get_db)):
    success = delete_order(db, order_id)
    if not success:
        raise HTTPException(status_code=404, detail="الطلب غير موجود")
    return {"message": "تم حذف الطلب بنجاح"}


@app.put("/order-app/api/v1/orders/{order_id}/read", status_code=status.HTTP_200_OK)
def mark_order_as_read(order_id: int, db: Session = Depends(get_db)):
    order = make_read(db, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="الطلب غير موجود")
    return order


# ------------------ نهاية كود إدارة الطلبات ------------------

from app.api.review_schemas import ReviewCreate, ReviewOut
from app.db.models import Review
from typing import List
from app.api.review_services import *

@app.post("/order-app/api/v1/reviews/", response_model=ReviewOut, status_code=status.HTTP_201_CREATED)
def create_review(review: ReviewCreate, db: Session = Depends(get_db)):
    try:
        new_review = create_new_review(review_data=review, db=db)
    
        return new_review
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Internal sever error {e}")

@app.get("/order-app/api/v1/reviews/products/", response_model=List[ReviewOut], status_code=status.HTTP_200_OK)
def get_all_reviews(product_id : int ,db: Session = Depends(get_db)):
    return get_reviews_by_product_id(db=db , product_id=product_id)

@app.get("/order-app/api/v1/reviews/{review_id}", response_model=ReviewOut, status_code=status.HTTP_200_OK)
def get_review(review_id: int, db: Session = Depends(get_db)):
    review = db.query(Review).filter(Review.review_id == review_id).first()
    if not review:
        raise HTTPException(status_code=404, detail="المراجعة غير موجودة")
    return review

@app.put("/order-app/api/v1/reviews/{review_id}", response_model=ReviewOut, status_code=status.HTTP_200_OK)
def update_review(review_id: int, updated_review: ReviewCreate, db: Session = Depends(get_db)):
    review = db.query(Review).filter(Review.review_id == review_id).first()
    if not review:
        raise HTTPException(status_code=404, detail="المراجعة غير موجودة")
    review.reviewer_name = updated_review.reviewer_name
    review.rate = updated_review.rate
    review.comment = updated_review.comment
    db.commit()
    db.refresh(review)
    return review

@app.delete("/order-app/api/v1/reviews/{review_id}", status_code=status.HTTP_200_OK)
def delete_review(review_id: int, db: Session = Depends(get_db)):
    review = db.query(Review).filter(Review.review_id == review_id).first()
    if not review:
        raise HTTPException(status_code=404, detail="المراجعة غير موجودة")
    db.delete(review)
    db.commit()
    return {"message": "تم حذف المراجعة بنجاح"}


# ------------------ نقاط نهاية إدارة المخزون ------------------

from app.api.poroduct_inventory_schema import *


@app.post("/order-app/api/v1/inventory/", response_model=ProductInventoryOut, status_code=status.HTTP_201_CREATED,
          summary="إنشاء بند مخزون جديد",
          description="يضيف بند مخزون جديد لتركيبة منتج ولون ومقاس محددة. يجب أن تكون تركيبة المنتج واللون والمقاس فريدة.")
def create_inventory_item(
    inventory_item: ProductInventoryCreate,
    db: Session = Depends(get_db)
):
    try:
        db_item = ProductInventory(**inventory_item.dict())
        db.add(db_item)
        db.commit()
        db.refresh(db_item)
        logger.info(f"تم إنشاء بند مخزون جديد: {db_item.product_inventory_id}")
        return db_item
    except IntegrityError as e:
        db.rollback()
        # التعامل مع خطأ UniqueConstraint
        if "unique constraint" in str(e).lower():
            logger.warning(f"محاولة إنشاء بند مخزون مكرر: Product ID {inventory_item.product_id}, Color {inventory_item.color}, Size {inventory_item.size}")
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"بند المخزون لهذه التركيبة (المنتج, اللون, المقاس) موجود بالفعل. استخدم نقطة التحديث لتغيير الكمية."
            )
        else:
            logger.error(f"خطأ في قاعدة البيانات عند إنشاء بند مخزون: {e}", exc_info=True)
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="خطأ في قاعدة البيانات")
    except Exception as e:
        logger.error(f"خطأ غير متوقع عند إنشاء بند مخزون: {e}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"خطأ داخلي في الخادم: {e}")
    
    
    

@app.get("/order-app/api/v1/inventory/{item_id}", response_model=ProductInventoryOut, status_code=status.HTTP_200_OK,
         summary="جلب بند مخزون بواسطة المعرف",
         description="يسترد تفاصيل بند مخزون محدد باستخدام معرفه الفريد.")
def get_inventory_item_by_id(
    item_id: int = Path(..., description="معرف بند المخزون الفريد"),
    db: Session = Depends(get_db)
):
    db_item = db.query(ProductInventory).filter(ProductInventory.product_inventory_id == item_id).first()
    if db_item is None:
        logger.warning(f"طلب بند مخزون غير موجود: ID {item_id}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="بند المخزون غير موجود")
    return db_item




@app.get("/order-app/api/v1/inventory/products/{product_id}", response_model=List[ProductInventoryOut], status_code=status.HTTP_200_OK,
         summary="جلب كل بنود المخزون لمنتج معين",
         description="يسترد قائمة بكل بنود المخزون (ألوان ومقاسات مختلفة) لمنتج معين باستخدام معرف المنتج.")
def get_inventory_by_product_id(
    product_id: int = Path(..., description="معرف المنتج الذي ترغب في جلب بنود المخزون الخاصة به"),
    db: Session = Depends(get_db)
):
    items = db.query(ProductInventory).filter(ProductInventory.product_id == product_id).all()
    if not items:
        logger.info(f"لا يوجد مخزون للمنتج ID: {product_id}")
        # يمكن اعتبار 200 مع قائمة فارغة OK، أو 404 إذا كان المنتج نفسه غير موجود
        # هنا نعود بقائمة فارغة إذا لم يتم العثور على بنود مخزون لهذا المنتج.
        return [] 
    return items





@app.patch("/order-app/api/v1/inventory/{item_id}", response_model=ProductInventoryOut, status_code=status.HTTP_200_OK,
           summary="تحديث الكمية في بند مخزون",
           description="يقوم بتحديث الكمية المتاحة لبند مخزون معين بحيث يتم استقبال الكمية المطلوبة وانقاصها من المخزون الكلي.")
def update_inventory_quantity(
    item_id: int = Path(..., description="معرف بند المخزون الفريد المراد تحديثه"),
    inventory_update: ProductInventoryUpdate = Body(..., description="بيانات التحديث (الكمية الجديدة)."),
    db: Session = Depends(get_db)
):
    db_item = db.query(ProductInventory).filter(ProductInventory.product_inventory_id == item_id).first()
    if db_item is None:
        logger.warning(f"محاولة تحديث بند مخزون غير موجود: ID {item_id}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="بند المخزون غير موجود")
    
    if db_item.quantity - inventory_update.ordered_quantity < 0:
        # يمكن هنا إضافة منطق للتحقق من أن الكمية الجديدة لا تقل عن 0
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="الكمية لا يمكن أن تكون سالبة.")
    db_item.quantity = db_item.quantity - inventory_update.ordered_quantity
    
    try:
        db.commit()
        db.refresh(db_item)
        logger.info(f"تم تحديث الكمية لبند المخزون {item_id} إلى {db_item.quantity}")
        return db_item
    except Exception as e:
        db.rollback()
        logger.error(f"خطأ عند تحديث بند المخزون {item_id}: {e}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"خطأ في قاعدة البيانات: {e}")
    
    
    
    

@app.delete("/order-app/api/v1/inventory/{item_id}", status_code=status.HTTP_200_OK,
            summary="حذف بند مخزون",
            description="يقوم بحذف بند مخزون محدد من قاعدة البيانات.")
def delete_inventory_item(
    item_id: int = Path(..., description="معرف بند المخزون الفريد المراد حذفه"),
    db: Session = Depends(get_db)
):
    db_item = db.query(ProductInventory).filter(ProductInventory.product_inventory_id == item_id).first()
    if db_item is None:
        logger.warning(f"محاولة حذف بند مخزون غير موجود: ID {item_id}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="بند المخزون غير موجود")
    
    try:
        db.delete(db_item)
        db.commit()
        logger.info(f"تم حذف بند المخزون: {item_id}")
        return {"message": "تم حذف بند المخزون بنجاح"}
    except Exception as e:
        db.rollback()
        logger.error(f"خطأ عند حذف بند المخزون {item_id}: {e}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"خطأ في قاعدة البيانات: {e}")




#------------------------ Products Endpoints by mongoDB------------------------


@app.get("/order-app/api/v1/products", response_model=List[Product], status_code=status.HTTP_200_OK,
         summary="جلب كل المنتجات",
         description="يسترد قائمة بكل المنتجات في قاعدة البيانات.")
async def get_all_products_from_db():
    return await get_all_products()


@app.get("/order-app/api/v1/products/", response_model=Product, status_code=status.HTTP_200_OK,
         summary="جلب منتج بواسطة المعرف",
         description="يسترد تفاصيل منتج محدد باستخدام معرفه الفريد.")
async def get_product_by_id_from_db(product_id: int):
    try:
    
        product = await get_product_by_id(product_id)
        if product:
            return product
        else :
            return {"msg" : "Product not found"}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"{e}")


@app.post("/order-app/api/v1/products/", response_model=Product, status_code=status.HTTP_201_CREATED,
          summary="إنشاء منتج جديد",
          description="يضيف منتج جديد إلى قاعدة البيانات.")
async def create_product_in_db(product: Product):
    try:
        return await add_product(product)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"{e}")



@app.put("/order-app/api/v1/products/{product_id}", response_model=Product, status_code=status.HTTP_200_OK,
          summary="تحديث منتج",
          description="يقوم بتحديث تفاصيل منتج محدد باستخدام معرفه الفريد.")
async def update_product_in_db(product_id: int, product: Product):
    return await update_product(product_id, product)


@app.delete("/order-app/api/v1/products/{product_id}", status_code=status.HTTP_200_OK,
             summary="حذف منتج",
             description="يقوم بحذف منتج محدد من قاعدة البيانات.")
async def delete_product_in_db(product_id: int):
    return await delete_product(product_id)
