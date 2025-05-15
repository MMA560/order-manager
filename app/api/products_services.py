from app.db.firestore_db_async import products_collection
from app.api.product_schema_mongo import Product
from typing import List, Optional

# Get all products
async def get_all_products() -> List[Product]:
    docs = products_collection.stream()
    result = []
    async for doc in docs:
        data = doc.to_dict()
        result.append(Product(**data))
    return result

# Get product by ID
async def get_product_by_id(product_id: int) -> Optional[Product]:
    query = products_collection.where("id", "==", product_id).limit(1)
    docs = query.stream()
    async for doc in docs:
        return Product(**doc.to_dict())
    return None

# Add product
async def add_product(product: Product) -> Product:
    product_dict = product.dict()
    await products_collection.add(product_dict)
    return product

# Update product by ID
async def update_product(product_id: int, product: Product) -> Optional[Product]:
    query = products_collection.where("id", "==", product_id).limit(1)
    docs = query.stream()
    async for doc in docs:
        await doc.reference.update(product.dict(exclude_unset=True))
        updated_data = await doc.reference.get()
        return Product(**updated_data.to_dict())
    return None

# Delete product by ID
async def delete_product(product_id: int) -> bool:
    query = products_collection.where("id", "==", product_id).limit(1)
    docs = query.stream()
    async for doc in docs:
        await doc.reference.delete()
        return True
    return False
