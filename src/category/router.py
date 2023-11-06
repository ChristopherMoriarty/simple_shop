from typing import List
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError, NoResultFound

from database import get_async_session

from category.schemas import CategoryCreate, CategoryRead, CategoryUpdate
from category.utils import (
    create_category,
    delete_category,
    update_category,
    get_categories_for_products,
    get_categories_with_product_count,
)

from exceptions import basic_exception


router = APIRouter()


@router.post("", response_model=dict)
async def category_create(
    category: CategoryCreate, session: AsyncSession = Depends(get_async_session)
):
    try:
        db_category = await create_category(session=session, category_data=category)

        return {
            "status": "success",
            "data": CategoryRead.model_validate(db_category),
            "detail": None,
        }
    except IntegrityError:
        await session.rollback()
        await basic_exception(status_code=400, message="Parent category does not exist")
    except Exception:
        await session.rollback()
        await basic_exception(status_code=500, message="Error while creating category")


@router.patch("", response_model=dict)
async def category_update(
    category_id: int,
    category: CategoryUpdate,
    session: AsyncSession = Depends(get_async_session),
):
    try:
        db_category = await update_category(
            session=session, category_id=category_id, new_data=category
        )

        return {
            "status": "success",
            "data": CategoryRead.model_validate(db_category),
            "detail": None,
        }
    except NoResultFound:
        await session.rollback()
        await basic_exception(status_code=404, message="Category does not exist")
    except IntegrityError:
        await session.rollback()
        await basic_exception(status_code=400, message="Parent category does not exist")
    except Exception:
        await session.rollback()
        await basic_exception(status_code=500, message="Error while creating category")


@router.delete("", response_model=dict)
async def category_delete(
    category_id: int, session: AsyncSession = Depends(get_async_session)
):
    try:
        db_category = await delete_category(session=session, category_id=category_id)

        if db_category is None:
            status_code = 404
            message = "Category not found"

        return {
            "status": "success",
            "data": CategoryRead.model_validate(db_category),
            "detail": None,
        }
    except NoResultFound:
        await session.rollback()
        await basic_exception(status_code=404, message="Category does not exist")
    except Exception:
        await session.rollback()
        await basic_exception(status_code=500, message="Error while creating category")


@router.get("/by_product_ids", response_model=dict)
async def categories_by_product_ids(
    product_ids: List[int] = Query(), session: AsyncSession = Depends(get_async_session)
):
    try:
        categories = await get_categories_for_products(
            session=session, product_ids=product_ids
        )

        if len(categories) != len(product_ids):
            raise NoResultFound

        return {
            "status": "success",
            "data": [CategoryRead.model_validate(category) for category in categories],
            "detail": None,
        }
    except NoResultFound:
        await session.rollback()
        await basic_exception(status_code=404, message="One or more product not found")
    except Exception:
        await session.rollback()
        await basic_exception(status_code=500, message="Error while getting categories")


@router.get("/with_product_count", response_model=dict)
async def categories_with_product_count(
    category_ids: List[int] = Query(),
    session: AsyncSession = Depends(get_async_session),
):
    try:
        categories = await get_categories_with_product_count(
            session=session, category_ids=category_ids
        )

        retrieved_category_ids = [category["category_id"] for category in categories]

        for cat_id in category_ids:
            if cat_id not in retrieved_category_ids:
                raise NoResultFound

        return {"status": "success", "data": categories, "detail": None}
    except NoResultFound:
        await session.rollback()
        await basic_exception(status_code=404, message="One or more category not found")
    except Exception:
        await session.rollback()
        await basic_exception(status_code=500, message="Error while getting categories")
