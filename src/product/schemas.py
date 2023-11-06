from typing import List, Optional
from pydantic import BaseModel


class ProductBase(BaseModel):
    name: str
    price: float
    category_ids: Optional[List[int]] = None


class ProductCreate(ProductBase):
    pass


class ProductRead(ProductBase):
    id: int

    class Config:
        from_attributes = True


class ProductUpdate(ProductBase):
    name: Optional[str]
    price: Optional[float]
    category_ids: Optional[List[int]] = None
