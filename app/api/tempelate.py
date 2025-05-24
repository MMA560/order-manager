# HTML Email Template

from app.api.schemas.order_schemas import OrderCreate

def generate_order_email_html(order_data: OrderCreate) -> str:
    return f"""
    <html dir="rtl">
    <head>
        <style>
            body {{
                font-family: 'Cairo', 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background-color: #f4f4f4;
                padding: 40px;
                color: #222;
                text-align: right;
            }}
            .card {{
                background-color: #fff;
                border: 2px solid #ddd;
                border-radius: 16px;
                box-shadow: 0 6px 16px rgba(0,0,0,0.15);
                max-width: 700px;
                margin: auto;
                padding: 40px;
            }}
            .header {{
                border-bottom: 3px solid #4CAF50;
                margin-bottom: 30px;
                padding-bottom: 15px;
            }}
            .header h2 {{
                color: #4CAF50;
                margin: 0;
                font-size: 26px;
            }}
            .info {{
                line-height: 2;
                font-size: 18px;
            }}
            .info .label {{
                display: inline-block;
                min-width: 160px;
                font-weight: 700;
                color: #222;
                font-size: 18px;
            }}
            .divider {{
                margin: 35px 0;
                border-top: 2px dashed #ccc;
            }}
            .footer {{
                margin-top: 30px;
                font-size: 16px;
                color: #777;
                text-align: center;
            }}
            .total {{
                font-size: 22px;
                font-weight: bold;
                color: #000;
            }}
        </style>
    </head>
    <body>
        <div class="card">
            <div class="header">
                <h2>📦 بوليصة شحن - Order Invoice</h2>
            </div>
            <div class="info" dir="rtl">
                <p><span class="label">الاسم:</span> {order_data.name}</p>
                <p><span class="label">رقم الهاتف:</span> {order_data.phone}</p>
                <p><span class="label">رقم إضافي:</span> {order_data.second_phone or 'لا يوجد'}</p>
                <p><span class="label">الإيميل:</span> {order_data.email or 'لا يوجد'}</p>
                <p><span class="label">العنوان:</span> {order_data.address}, {order_data.city}, {order_data.state}</p>
                <p><span class="label">المحافظة</span> {order_data.state }</p>
                <p><span class="label">المدينة</span> {order_data.city }</p>

                <div class="divider"></div>

                <p><span class="label">المنتج:</span> {order_data.product}</p>
                <p><span class="label">اللون:</span> {order_data.color}</p>
                <p><span class="label">المقاس:</span> {order_data.size}</p>
                <p><span class="label">طريقة الشحن:</span> {order_data.shipping}</p>
                <p><span class="label">الملاحظات:</span> {order_data.notes or 'لا يوجد'}</p>

                <div class="divider"></div>

                <p class="total"><span class="label">💰 السعر الإجمالي:</span> {order_data.total_cost} جنيه</p>
            </div>
            <div class="footer">
                تم إنشاء هذا الطلب تلقائيًا بواسطة نظام الطلبات الخاص بنا.<br>شكرًا لثقتكم بنا 🌟
            </div>
        </div>
    </body>
    </html>
    """
from datetime import datetime

# تحويل الوقت لصيغة يوم-شهر-سنة وساعة
def format_datetime_arabic():
    months_ar = [
        "يناير", "فبراير", "مارس", "أبريل", "مايو", "يونيو",
        "يوليو", "أغسطس", "سبتمبر", "أكتوبر", "نوفمبر", "ديسمبر"
    ]
    now = datetime.now()
    day = now.day
    month = months_ar[now.month - 1]
    year = now.year
    hour = now.strftime('%I')  # 12-hour format
    minute = now.strftime('%M')
    am_pm = 'صباحاً' if now.strftime('%p') == 'AM' else 'مساءً'
    return f"{day} {month} {year} - {hour}:{minute} {am_pm}"
