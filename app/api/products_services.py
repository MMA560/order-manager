from app.db.firestore_db_async import get_products_collection
from app.api.product_schema_mongo import *
from google.cloud.firestore import FieldFilter
from typing import List, Optional

async def get_all_products() -> List[ProductOut]:
    try:
        simplified_products = []
        products_collection = get_products_collection()

        async for doc in products_collection.stream():
            data = doc.to_dict()
            product = Product(**data)
            simplified_dict = simplify_product_for_card(product.dict())
            simplified_products.append(ProductOut(**simplified_dict))

        return simplified_products
    except Exception as e:
        print(f"Error in get_all_products: {e}")
        raise

async def get_product_by_id(product_id: int) -> Optional[Product]:
    try:
        # الحصول على مجموعة المنتجات لكل طلب
        products_collection = get_products_collection()
        query = products_collection.where(filter=FieldFilter("id", "==", product_id)).limit(1)
        async for doc in query.stream():
            return Product(**doc.to_dict())
        return None
    except Exception as e:
        print(f"Error in get_product_by_id for ID {product_id}: {e}")
        raise

async def add_product(product: Product) -> Product:
    try:
        # الحصول على مجموعة المنتجات لكل طلب
        products_collection = get_products_collection()
        product_dict = product.dict()
        await products_collection.add(product_dict)
        return product
    except Exception as e:
        print(f"Error in add_product: {e}")
        raise

async def update_product(product_id: int, product: Product) -> Optional[Product]:
    try:
        # الحصول على مجموعة المنتجات لكل طلب
        products_collection = get_products_collection()
        query = products_collection.where(filter=FieldFilter("id", "==", product_id)).limit(1)
        product_data = None
        doc_ref = None
        
        async for doc in query.stream():
            # استخدم product.model_dump(exclude_unset=True) إذا كنت تستخدم Pydantic V2+
            product_dict = product.dict(exclude_unset=True)
            doc_ref = doc.reference
            await doc_ref.update(product_dict)
            
        if doc_ref:
            doc_snapshot = await doc_ref.get()
            return Product(**doc_snapshot.to_dict())
        return None
    except Exception as e:
        print(f"Error in update_product for ID {product_id}: {e}")
        raise

async def delete_product(product_id: int) -> bool:
    try:
        # الحصول على مجموعة المنتجات لكل طلب
        products_collection = get_products_collection()
        query = products_collection.where(filter=FieldFilter("id", "==", product_id)).limit(1)
        deleted = False
        
        async for doc in query.stream():
            await doc.reference.delete()
            deleted = True
            
        return deleted
    except Exception as e:
        print(f"Error in delete_product for ID {product_id}: {e}")
        raise
    
    
    
    
    
    
    
#=======================================================================

def simplify_product_for_card(product: dict) -> dict:
    """
    تبسيط كائن المنتج لكرت العرض:
    - mainImage: أول صورة لأول لون من المعرض.
    - tags: قائمة مختصرة فقط بـ id.
    - لا يتم إرجاع الحقول: availableColors, availableSizes, galleryImages
    """
    simplified = {
        "id": product.get("id"),
        "name": product.get("name"),
        "description": product.get("description"),
        "price": product.get("price"),
        "oldPrice": product.get("oldPrice"),
        "discount": product.get("discount"),
        "tags": [{"id": tag.get("id")} for tag in product.get("tags", []) if tag and tag.get("id")],
        "mainImage": None
    }

    # استخراج أول صورة من أول لون
    available_colors = product.get("availableColors", [])
    gallery_images = product.get("galleryImages", {})

    if available_colors:
        first_color_value = available_colors[0].get("value")
        images_for_color = gallery_images.get(first_color_value)
        if images_for_color and len(images_for_color) > 0:
            simplified["mainImage"] = images_for_color[0].get("src")

    return simplified