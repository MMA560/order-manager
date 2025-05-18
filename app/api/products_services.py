# app/api/products_services.py

from app.db.firestore_db_async import products_collection
from app.api.product_schema_mongo import Product
from google.cloud.firestore import FieldFilter
from typing import List, Optional

async def get_all_products() -> List[Product]:
    try:
        products = []
        async for doc in products_collection.stream():
            data = doc.to_dict()
            products.append(Product(**data))
        return products
    except Exception as e:
        print(f"Error in get_all_products: {e}")
        raise

async def get_product_by_id(product_id: int) -> Optional[Product]:
    try:
        query = products_collection.where(filter=FieldFilter("id", "==", product_id)).limit(1)
        async for doc in query.stream():
            return Product(**doc.to_dict())
        return None
    except Exception as e:
        print(f"Error in get_product_by_id for ID {product_id}: {e}")
        raise

async def add_product(product: Product) -> Product:
    try:
        product_dict = product.dict()
        await products_collection.add(product_dict)
        return product
    except Exception as e:
        print(f"Error in add_product: {e}")
        raise

async def update_product(product_id: int, product: Product) -> Optional[Product]:
    try:
        query = products_collection.where(filter=FieldFilter("id", "==", product_id)).limit(1)
        async for doc in query.stream():
            # استخدم product.model_dump(exclude_unset=True) إذا كنت تستخدم Pydantic V2+
            await doc.reference.update(product.dict(exclude_unset=True))
            updated_data = await doc.reference.get()
            return Product(**updated_data.to_dict())
        return None
    except Exception as e:
        print(f"Error in update_product for ID {product_id}: {e}")
        raise

async def delete_product(product_id: int) -> bool:
    try:
        query = products_collection.where(filter=FieldFilter("id", "==", product_id)).limit(1)
        async for doc in query.stream():
            await doc.reference.delete()
            return True
        return False
    except Exception as e:
        print(f"Error in delete_product for ID {product_id}: {e}")
        raise