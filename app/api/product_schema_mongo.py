from pydantic import BaseModel
from typing import List, Dict, Optional

class Tag(BaseModel):
    name: str
    id: str

    class Config:
        from_attributes = True

class AvailableSize(BaseModel):
    value: str
    label: str

    class Config:
        from_attributes = True

class AvailableColor(BaseModel):
    value: str
    label: str
    image: str

    class Config:
        from_attributes = True

class GalleryImage(BaseModel):
    src: str
    alt: str

    class Config:
        from_attributes = True

class DetailsSection(BaseModel):
    title: str
    items: List[str]

    class Config:
        from_attributes = True

class Highlight(BaseModel):
    title: str
    description: str
    iconName: str

    class Config:
        from_attributes = True

class VideoInfo(BaseModel):
    title: str
    videoUrl: str
    thumbnail: str
    overlayText: str
    descriptionTitle: str
    description: str
    features: List[str]

    class Config:
        from_attributes = True

class Faq(BaseModel):
    question: str
    answer: str

    class Config:
        from_attributes = True

class Product(BaseModel):
    id: int
    name: str
    nameEn: str
    label: str
    description: str
    price: float
    oldPrice: float
    discount: int
    tags: List[Tag]
    availableSizes: List[AvailableSize]
    availableColors: List[AvailableColor]
    galleryImages: Dict[str, List[GalleryImage]]
    detailsSections: List[DetailsSection]
    highlights: List[Highlight]
    videoInfo: VideoInfo
    faqs: List[Faq]
    inventory: Dict
    inventoryIds: Dict

    class Config:
        from_attributes = True
        

class TagOut(BaseModel):
    id: str

    class Config:
        from_attributes = True

# ✅ نسخة مبسطة جداً مع mainImage يحتوي على أول صورة فقط
class ProductOut(BaseModel):
    id: int
    name: str
    description: str
    price: float
    oldPrice: Optional[float] = None
    discount: Optional[int] = None
    tags: Optional[List[TagOut]] = []
    mainImage: Optional[str] = None  # أول صورة لأول لون في المعرض

    class Config:
        from_attributes = True