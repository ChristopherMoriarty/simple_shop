from fastapi import FastAPI

from category.router import router as category_router
from product.router import router as product_router


app = FastAPI(
    title="simple_shop"
)

app.include_router(
    category_router,
    prefix="/api/v1.0/categories",
    tags=["Categories"]
)

app.include_router(
    product_router,
    prefix="/api/v1.0/products",
    tags=["Products"]
)