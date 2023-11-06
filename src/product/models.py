from sqlalchemy import Column, ForeignKey, Integer, String, Float, Table
from sqlalchemy.orm import relationship
from database import Base


class Product(Base):
    __tablename__ = "product"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    price = Column(Float, nullable=False)

    categories = relationship(
        "Category", secondary="product_category_association", back_populates="products"
    )


product_category_association = Table(
    "product_category_association",
    Base.metadata,
    Column("product_id", Integer, ForeignKey("product.id")),
    Column("category_id", Integer, ForeignKey("category.id")),
)
