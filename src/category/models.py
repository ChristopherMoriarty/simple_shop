from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from database import Base


class Category(Base):
    __tablename__ = "category"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    parent_id = Column(Integer, ForeignKey("category.id"), nullable=True)

    parent_category = relationship(
        "Category", remote_side=[id], back_populates="child_categories"
    )
    child_categories = relationship("Category", back_populates="parent_category")

    products = relationship(
        "Product", secondary="product_category_association", back_populates="categories"
    )

    def __init__(self, name, parent_id=None):
        self.name = name
        self.parent_id = parent_id
