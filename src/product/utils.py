from collections import defaultdict
from typing import List, Optional
from sqlalchemy import distinct, or_, select, func
from sqlalchemy.orm import joinedload, aliased
from sqlalchemy.ext.asyncio import AsyncSession

from category.models import Category

from .models import Product, product_category_association
from .schemas import ProductCreate, ProductRead, ProductUpdate


async def create_product(session: AsyncSession, product: ProductCreate) -> ProductRead:
    db_product = Product(name=product.name, price=product.price)
    session.add(db_product)
    await session.flush()

    category_ids = []
    if product.category_ids:
        for cat_id in product.category_ids:
            association = product_category_association.insert().values(
                product_id=db_product.id, category_id=cat_id
            )
            await session.execute(association)
            category_ids.append(cat_id)

    await session.commit()

    response = ProductRead(
        id=db_product.id,
        name=db_product.name,
        price=db_product.price,
        category_ids=category_ids,
    )
    return response


async def update_product(
    session: AsyncSession, product_id: int, product: ProductUpdate
) -> ProductRead:
    stmt = select(Product).filter(Product.id == product_id)
    db_product = await session.execute(stmt)
    db_product = db_product.scalar_one()

    db_product.name = product.name
    db_product.price = product.price

    if product.category_ids is not None:
        await session.execute(
            product_category_association.delete().where(
                product_category_association.c.product_id == db_product.id
            )
        )

        for cat_id in product.category_ids:
            association = product_category_association.insert().values(
                product_id=db_product.id, category_id=cat_id
            )
            await session.execute(association)

    await session.commit()
    await session.refresh(db_product)

    response = ProductRead(
        id=db_product.id,
        name=db_product.name,
        price=db_product.price,
        category_ids=product.category_ids if product.category_ids is not None else [],
    )
    return response


async def delete_product(session: AsyncSession, product_id: int) -> ProductRead:
    product_stmt = select(Product).where(Product.id == product_id)
    db_product = await session.execute(product_stmt)
    db_product = db_product.scalar_one()

    categories_stmt = select(product_category_association.c.category_id).where(
        product_category_association.c.product_id == product_id
    )
    category_ids_result = await session.execute(categories_stmt)
    category_ids = [row.category_id for row in category_ids_result]

    await session.delete(db_product)
    await session.commit()

    response = ProductRead(
        id=db_product.id,
        name=db_product.name,
        price=db_product.price,
        category_ids=category_ids,
    )

    return response


async def get_products_by_category(session: AsyncSession, category_id: int):
    child_category = aliased(Category)

    stmt = (
        select(Product, Category.id.label("category_id"))
        .join(
            product_category_association,
            Product.id == product_category_association.c.product_id,
        )
        .join(Category, product_category_association.c.category_id == Category.id)
        .outerjoin(child_category, Category.id == child_category.parent_id)
        .where((Category.id == category_id) | (child_category.id == category_id))
    )

    result = await session.execute(stmt)

    # Create dict with products and their categories by defaultdict
    product_category_map = defaultdict(list)
    for product, category_id in result:
        product_category_map[product].append(category_id)

    return [
        {
            "id": product.id,
            "name": product.name,
            "price": product.price,
            "category_ids": category_ids,
        }
        for product, category_ids in product_category_map.items()
    ]


async def get_unique_products_count(
    session: AsyncSession, category_ids: List[int]
) -> int:
    existing_categories_count = await session.execute(
        select(func.count(Category.id)).where(Category.id.in_(category_ids))
    )
    existing_categories_count = existing_categories_count.scalar()

    if existing_categories_count < len(category_ids):
        return None

    stmt = select(distinct(product_category_association.c.product_id)).where(
        product_category_association.c.category_id.in_(category_ids)
    )

    result = await session.execute(stmt)
    unique_products_ids = [row[0] for row in result]

    return len(unique_products_ids)
