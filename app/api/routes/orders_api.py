from fastapi import APIRouter, HTTPException, status, Depends, Path, Body

from sqlalchemy.orm import Session

from email.mime.multipart import MIMEMultipart

from email.mime.text import MIMEText

import smtplib

import logging

from typing import List

from app.api.tempelate import generate_order_email_html, format_datetime_arabic

from app.api.schemas.order_schemas import *

from app.db.database import get_db

from app.api.services.order_services import *

from app.db.models import Order  # Import the Order model


router = APIRouter(

    prefix="/order-app/api/v1",

    tags=["orders"],

)


# إعدادات الإيميل (استخدم .env في التطبيق الحقيقي لتأمين بيانات الاعتماد)

SMTP_SERVER = "smtp.gmail.com"

SMTP_PORT = 587

EMAIL_ADDRESS = "zxz01144@gmail.com"

EMAIL_PASSWORD = "ikbw fgvp xmno fvlg"


logger = logging.getLogger(__name__)


@router.post("/create-order/", status_code=status.HTTP_200_OK)

def create_order_endpoint(order_data: OrderCreate, to_email: str, db: Session = Depends(get_db)):

    order = create_order(db=db, order_data=order_data)

    html_content = generate_order_email_html(order_data)

    msg = MIMEMultipart("alternative")

    msg["Subject"] = f"تأكيد طلب {order_data.name}!- {format_datetime_arabic()}"

    msg["From"] = "Rush Kicks"

    msg["To"] = to_email

    msg.attach(MIMEText("تم استلام طلبك بنجاح. التفاصيل موجودة بالأسفل.", "plain"))

    msg.attach(MIMEText(html_content, "html"))


    try:

        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:

            server.starttls()

            server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)

            server.send_message(msg)

    except Exception as e:

        logger.error(f"فشل إرسال البريد الإلكتروني للطلب (ID: {order.order_id if order else 'غير متوفر'}): {e}", exc_info=True)

        raise HTTPException(status_code=500, detail=f"تم حفظ الطلب ولكن فشل إرسال الإيميل: {str(e)}")


    return order


@router.get("/{order_id}", status_code=status.HTTP_200_OK, response_model=OrderOut)

def get_order(order_id: int = Path(..., description="رقم الطلب"), db: Session = Depends(get_db)):

    order = get_order_by_id(db, order_id)

    if not order:

        raise HTTPException(status_code=404, detail="الطلب غير موجود")

    return order


@router.get("/", status_code=status.HTTP_200_OK, response_model=List[OrderOut])

def get_orders(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):

    return get_all_orders(db, skip=skip, limit=limit)


@router.put("/{order_id}", status_code=status.HTTP_200_OK, response_model=OrderOut)

def update_order_endpoint(

    order_id: int,

    order_update: OrderUpdate = Body(...),

    db: Session = Depends(get_db)

):

    updated_order = update_order(db, order_id, order_update)

    if not updated_order:

        raise HTTPException(status_code=404, detail="الطلب غير موجود")

    return updated_order


@router.delete("/{order_id}", status_code=status.HTTP_200_OK)

def delete_order_endpoint(order_id: int, db: Session = Depends(get_db)):

    success = delete_order(db, order_id)

    if not success:

        raise HTTPException(status_code=404, detail="الطلب غير موجود")

    return {"message": "تم حذف الطلب بنجاح"}


@router.put("/{order_id}/read", status_code=status.HTTP_200_OK, response_model=OrderOut)

def mark_order_as_read(order_id: int, db: Session = Depends(get_db)):

    order = make_read(db, order_id)

    if not order:

        raise HTTPException(status_code=404, detail="الطلب غير موجود")

    return order