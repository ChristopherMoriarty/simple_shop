from typing import List

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from category.schemas import CategoryCreate, CategoryUpdate
from category.models import Category

from product.models import Product, product_category_association


async def get_category(session: AsyncSession, category_id: int) -> Category:
    stmt = select(Category).filter_by(id=category_id)
    category = await session.execute(stmt)

    return category.scalars().first()


async def create_category(
    session: AsyncSession, category_data: CategoryCreate
) -> Category:
    category = Category(**category_data.model_dump())
    session.add(category)

    await session.commit()
    await session.refresh(category)

    return category


async def update_category(
    session: AsyncSession, category_id: int, new_data: CategoryUpdate
) -> Category:
    stmt = await session.execute(select(Category).filter_by(id=category_id))
    category = stmt.scalar_one()

    if category:
        for key, value in new_data.model_dump().items():
            setattr(category, key, value)

        await session.commit()
        await session.refresh(category)

    return category


async def delete_category(session: AsyncSession, category_id: int) -> Category:
    stmt = await session.execute(select(Category).filter_by(id=category_id))
    category = stmt.scalar_one()

    if category:
        await session.delete(category)
        await session.commit()

    return category


async def get_categories_for_products(
    session: AsyncSession, product_ids: List[int]
) -> List[Category]:
    stmt = (
        select(Category)
        .join(
            product_category_association,
            Category.id == product_category_association.c.category_id,
        )
        .where(product_category_association.c.product_id.in_(product_ids))
        .distinct()
    )

    db_category = await session.execute(stmt)
    categories = db_category.scalars().all()
    return categories


async def get_categories_with_product_count(
    session: AsyncSession, category_ids: List[int]
):
    stmt = (
        select(
            Category.id.label("category_id"),
            Category.name.label("category_name"),
            func.coalesce(func.count(Product.id), 0).label("products_count"),
        )
        .outerjoin(
            product_category_association,
            Category.id == product_category_association.c.category_id,
        )
        .outerjoin(Product, Product.id == product_category_association.c.product_id)
        .where(Category.id.in_(category_ids))
        .group_by(Category.id, Category.name)
    )

    result = await session.execute(stmt)

    return [
        {
            "category_id": row.category_id,
            "category_name": row.category_name,
            "products_count": row.products_count,
        }
        for row in result
    ]
