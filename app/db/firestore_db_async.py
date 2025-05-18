import os
import json
from google.cloud import firestore
from dotenv import load_dotenv
import google.oauth2.service_account

# تحميل متغيرات البيئة
load_dotenv()

# اسم متغير البيئة الذي يحتوي على محتوى JSON لمفتاح حساب الخدمة
CREDENTIALS_JSON_ENV_VAR = "GCP_FIREBASE_CREDENTIALS_JSON"

# دالة للحصول على بيانات الاعتماد
def get_credentials():
    # قراءة محتوى JSON من متغير البيئة
    credentials_json_string = os.getenv(CREDENTIALS_JSON_ENV_VAR)

    # تحقق من أن المتغير موجود وقيمته غير فارغة
    if not credentials_json_string:
        raise ValueError(
            f"Environment variable {CREDENTIALS_JSON_ENV_VAR} not set or is empty. "
            "Please ensure your .env file is correct and located in the project root, "
            "or that the environment variable is set on your hosting platform."
        )

    # تحليل سلسلة JSON إلى قاموس Python
    try:
        credentials_info = json.loads(credentials_json_string)
    except json.JSONDecodeError as e:
        raise ValueError(
            f"Failed to decode JSON from environment variable {CREDENTIALS_JSON_ENV_VAR}. "
            "Please check the JSON content in your .env file or environment variable settings for errors."
        ) from e

    # استخراج project_id من معلومات الاعتماد
    project_id = credentials_info.get('project_id')
    if not project_id:
        raise ValueError(
            f"Project ID not found in credentials JSON loaded from {CREDENTIALS_JSON_ENV_VAR}. "
            "Please ensure the 'project_id' field exists and is correct in your credentials JSON."
        )

    # إنشاء كائن بيانات الاعتماد من القاموس
    try:
        credentials = google.oauth2.service_account.Credentials.from_service_account_info(credentials_info)
        return credentials, project_id
    except Exception as e:
        raise RuntimeError(
            f"Failed to create Google Cloud credentials from the provided JSON info loaded from {CREDENTIALS_JSON_ENV_VAR}. "
            "Please check the 'private_key' field and ensure the entire JSON content is correct and not truncated."
        ) from e

# دالة للحصول على عميل Firestore
def get_firestore_client():
    credentials, project_id = get_credentials()
    return firestore.AsyncClient(credentials=credentials, project=project_id)

# دالة للحصول على مجموعة المنتجات
def get_products_collection():
    db = get_firestore_client()
    return db.collection("products")

print("Firestore module initialized successfully.")