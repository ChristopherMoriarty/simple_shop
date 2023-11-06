import sys
from faker import Faker
import asyncio
import random

from category.schemas import CategoryCreate
from category.utils import create_category

from product.schemas import ProductCreate
from product.utils import create_product

from database import get_async_session

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())


fake = Faker()

def generate_category_data(total: int):
    categories_data = []
    for _ in range(total // 2):
        category_data = CategoryCreate(
            name=fake.word()
        )
        categories_data.append(category_data)
    
    for i in range(1, total - (total // 2) + 1):
        category_data = CategoryCreate(
            name=fake.word(),
            parent_id=i
        )
        categories_data.append(category_data)

    return categories_data

def generate_product_data(cat_total: int, product_total: int):
    products_data = []
    for _ in range(product_total):
        product_data = ProductCreate(
            name=fake.word(),
            price=fake.pydecimal(left_digits=3, right_digits=2, positive=True, min_value=1, max_value=1000),
            category_ids=[random.randint(1, cat_total)]
        )
        products_data.append(product_data)
    
    return products_data
    


async def generate_data(category_total, product_total):
    async for session in get_async_session():
        categories_data = generate_category_data(category_total)
        product_data = generate_product_data(category_total, product_total)
        for data in categories_data:
            await create_category(session=session, category_data=data)
        for data in product_data:
            await create_product(session=session, product=data)



# Генерируем данные

# Добавляем данные в базу
asyncio.run(generate_data(10, 20))