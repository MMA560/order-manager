from fastapi import FastAPI, HTTPException, status, Depends, Path, Body
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib
from datetime import datetime

# استيرادات الوحدات المحلية الخاصة بك
from app.api.tempelate import *
from app.api.order_schemas import *
from app.db.database import get_db, Base, enigne
from app.api.order_services import *

import logging # <--- تم استيراد وحدة logging

# إعداد بسيط لـ logging
# في تطبيق حقيقي، يجب أن يكون لديك إعداد logging أكثر تعقيدًا في ملف منفصل
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__) # <--- الحصول على كائن logger لهذه الوحدة

# تهيئة قاعدة البيانات
Base.metadata.create_all(bind=enigne)

app = FastAPI(
    title="نظام إدارة الطلبات",
    description="API لحفظ الطلبات وإرسال تفاصيلها عبر البريد الإلكتروني بشكل احترافي.",
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
    return {"msg":"Welcome to Order App"}

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

@app.post("/order-app/api/v1/reviews/", response_model=ReviewOut, status_code=status.HTTP_201_CREATED)
def create_review(review: ReviewCreate, db: Session = Depends(get_db)):
    new_review = Review(
        reviewer_name=review.reviewer_name,
        rate=review.rate,
        comment=review.comment
    )
    db.add(new_review)
    db.commit()
    db.refresh(new_review)
    return new_review

@app.get("/order-app/api/v1/reviews/", response_model=List[ReviewOut], status_code=status.HTTP_200_OK)
def get_all_reviews(db: Session = Depends(get_db)):
    return db.query(Review).all()

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
