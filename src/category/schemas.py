from typing import Optional
from pydantic import BaseModel


class CategoryBase(BaseModel):
    name: str
    parent_id: Optional[int] = None


class CategoryCreate(CategoryBase):
    pass


class CategoryRead(CategoryBase):
    id: int

    class Config:
        from_attributes = True


class CategoryUpdate(CategoryBase):
    name: Optional[str] = None
