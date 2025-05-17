# app/services/push_token_service.py

from sqlalchemy.orm import Session
from app.db.models import PushToken
from app.api.token_schemas import PushTokenCreate

def create_push_token(db: Session, token_data: PushTokenCreate):
    token = PushToken(fcm_token=token_data.fcm_token)
    db.add(token)
    db.commit()
    db.refresh(token)
    return token



def get_all_push_tokens(db: Session):
    return db.query(PushToken).all()


#--------------------- Send Notifications ------------------
from firebase_admin import messaging
from sqlalchemy.orm import Session
import logging

logger = logging.getLogger(__name__)

def send_push_notification_to_token(
    db: Session,
    fcm_token: str,
    order_id: int,
    customer_name: str
) -> None:
    """
    إرسال إشعار إلى جهاز واحد باستخدام FCM Token.

    Args:
        db (Session): جلسة قاعدة البيانات (احتياطياً إن أردت استخدامها).
        fcm_token (str): التوكن الذي سيتم الإرسال إليه.
        order_id (int): رقم الطلب.
        customer_name (str): اسم الزبون لعرضه في نص الإشعار.
    """
    try:
        message = messaging.Message(
            notification=messaging.Notification(
                title="طلب جديد!",
                body=f"تم استلام طلب جديد من {customer_name}. رقم الطلب: {order_id}",
            ),
            data={
                "order_id": str(order_id),
                "action": "view_order",
            },
            token=fcm_token,
        )

        response = messaging.send(message)
        logger.info(f"تم إرسال إشعار بنجاح إلى التوكن ({fcm_token}) للطلب (ID: {order_id}).")

    except Exception as e:
        logger.error(f"فشل إرسال إشعار إلى التوكن ({fcm_token}) للطلب (ID: {order_id}): {e}", exc_info=True)
