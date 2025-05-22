from pydantic import BaseModel, Field

class FavoriteCreate(BaseModel):
    user_identifier: str = Field(..., description="معرف العميل (مثل معرف الكوكي)")
    product_id: int = Field(..., description="معرف المنتج المفضل")

    class Config:
        from_attributes = True
        