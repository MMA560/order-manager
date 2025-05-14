from pydantic import BaseModel
from typing import List, Dict

class Tag(BaseModel):
    name: str
    id: str

    class Config:
        arbitrary_types_allowed = True

class AvailableSize(BaseModel):
    value: str
    label: str

    class Config:
        arbitrary_types_allowed = True

class AvailableColor(BaseModel):
    value: str
    label: str
    image: str

    class Config:
        arbitrary_types_allowed = True

class GalleryImage(BaseModel):
    src: str
    alt: str

    class Config:
        arbitrary_types_allowed = True

class DetailsSection(BaseModel):
    title: str
    items: List[str]

    class Config:
        arbitrary_types_allowed = True

class Highlight(BaseModel):
    title: str
    description: str
    iconName: str

    class Config:
        arbitrary_types_allowed = True

class VideoInfo(BaseModel):
    title: str
    videoUrl: str
    thumbnail: str
    overlayText: str
    descriptionTitle: str
    description: str
    features: List[str]

    class Config:
        arbitrary_types_allowed = True

class Faq(BaseModel):
    question: str
    answer: str

    class Config:
        arbitrary_types_allowed = True

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
        arbitrary_types_allowed = True