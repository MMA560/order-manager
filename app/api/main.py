from fastapi import FastAPI, HTTPException, status, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib
from app.api.tempelate import *
from app.api.order_schemas import OrderCreate
from app.db.database import get_db, Base, enigne
from app.api.order_services import create_order as create_order_service
from datetime import datetime


from fastapi import FastAPI

Base.metadata.create_all(bind = enigne)

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


# إعدادات الإيميل (استخدم .env في التطبيق الحقيقي)
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
EMAIL_ADDRESS = "zxz01144@gmail.com"
EMAIL_PASSWORD = "ikbw fgvp xmno fvlg"

@app.get("/", status_code=status.HTTP_200_OK)
def root():
    return {"msg":"Welcome to Order App"}

@app.post("/order-app/api/v1/create-order/", status_code=status.HTTP_200_OK)
def create_order_endpoint(order_data: OrderCreate,to_email : str, db: Session = Depends(get_db)):
    # حفظ الطلب في قاعدة البيانات
    order = create_order_service(db=db, order_data=order_data)

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
        raise HTTPException(status_code=500, detail=f"تم حفظ الطلب ولكن فشل إرسال الإيميل: {str(e)}")

    return {"message": "تم إنشاء الطلب وإرسال الإيميل بنجاح"}
