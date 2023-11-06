from typing import List
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError, NoResultFound

from database import get_async_session

from product.schemas import ProductCreate, ProductRead, ProductUpdate
from product.utils import (
    create_product,
    delete_product,
    update_product,
    get_products_by_category,
    get_unique_products_count,
)

from exceptions import basic_exception


router = APIRouter()


@router.post("", response_model=dict)
async def product_create(
    product: ProductCreate, session: AsyncSession = Depends(get_async_session)
):
    try:
        db_product = await create_product(session=session, product=product)

        return {
            "status": "success",
            "data": ProductRead.model_validate(db_product),
            "detail": None,
        }
    except IntegrityError:
        await session.rollback()
        await basic_exception(
            status_code=400,
            message="One or more of the parent categories does not exist",
        )
    except Exception:
        await session.rollback()
        await basic_exception(status_code=500, message="Error while creating product")


@router.patch("", response_model=dict)
async def product_update(
    product_id: int,
    product: ProductUpdate,
    session: AsyncSession = Depends(get_async_session),
):
    try:
        db_product = await update_product(
            session=session, product_id=product_id, product=product
        )

        return {
            "status": "success",
            "data": ProductRead.model_validate(db_product),
            "detail": None,
        }
    except NoResultFound:
        await session.rollback()
        await basic_exception(status_code=404, message="Product does not exist")
    except IntegrityError:
        await session.rollback()
        await basic_exception(
            status_code=400,
            message="One or more of the parent categories does not exist",
        )
    except Exception:
        await session.rollback()
        await basic_exception(status_code=500, message="Error while creating product")


@router.delete("", response_model=dict)
async def product_delete(
    product_id: int, session: AsyncSession = Depends(get_async_session)
):
    try:
        db_product = await delete_product(session=session, product_id=product_id)

        return {
            "status": "success",
            "data": ProductRead.model_validate(db_product),
            "detail": None,
        }
    except NoResultFound:
        await session.rollback()
        await basic_exception(status_code=404, message="Product does not exist")
    except Exception:
        await session.rollback()
        await basic_exception(status_code=500, message="Error while creating product")


@router.get("/by_category_tree", response_model=dict)
async def get_products_by_category_tree(
    parent_category_id: int, session: AsyncSession = Depends(get_async_session)
):
    try:
        products = await get_products_by_category(
            session=session, category_id=parent_category_id
        )

        if not products:
            raise NoResultFound

        return {
            "status": "success",
            "data": [ProductRead.model_validate(product) for product in products],
            "detail": None,
        }
    except NoResultFound:
        await session.rollback()
        await basic_exception(status_code=404, message="Category does not exist")
    except Exception:
        await session.rollback()
        await basic_exception(status_code=500, message="Error while getting products")


@router.get("/number_of_unique_by_categories_ids")
async def get_number_of_unique_producrs(
    category_ids: List[int] = Query(),
    session: AsyncSession = Depends(get_async_session),
):
    try:
        products_count = await get_unique_products_count(
            session=session, category_ids=category_ids
        )

        if products_count is None:
            raise NoResultFound

        return {
            "status": "success",
            "data": {"unique_products_count": products_count},
            "detail": None,
        }
    except NoResultFound:
        await session.rollback()
        await basic_exception(
            status_code=404, message="One or more category does not exist"
        )
    except Exception:
        await session.rollback()
        await basic_exception(status_code=500, message="Error while getting products")
