import gino
from aiogram import types
from aiogram.dispatcher import FSMContext

from tgbot.data import config
import asyncio

from tgbot.keyboards.inline.gen_keyboard import KeyboardGen
from tgbot.utils.db_api.db_gino import db
from tgbot.utils.db_api.schemas.goods import Subcategory, Category, Product


async def get_parent_child():  # get child model with children attribute
    query = Subcategory.outerjoin(Category).select()
    parent = await query.gino.load(Category.distinct(Category.id).load(children=Subcategory)).all()
    return parent


async def get_child_parent(category_id: int):
    async with db.transaction():
        query = Subcategory.load(parent=Category).where(Category.id == category_id)
        result = await query.gino.all()
    return result


async def get_product(product_id: int):
    async with db.transaction():
        product = Product.load(parent=Subcategory)
        result = await product.where(Product.id == product_id).gino.first()
    return result


async def get_liked_product(liked_products_id: list, state: FSMContext):
    query_answer = []
    async with db.transaction():
        for product_id in liked_products_id:
            db_query = Product.load(parent=Subcategory)
            product = await db_query.where(Product.id == product_id).gino.first()
            async with state.proxy() as state_data:
                state_data["product_info"] = {"is_liked": 1}
                keyboard = KeyboardGen(product=product, data=state_data)
                markup = keyboard.build_product_kb()
            query_answer.append(
                types.InlineQueryResultArticle(
                    id=str(product.id),
                    title=product.title,
                    input_message_content=types.InputTextMessageContent(
                        message_text=f"<a href='{product.image}'>{product.title}</a>", parse_mode="HTML"
                    ),
                    reply_markup=markup,
                    description=str(product.price),
                    thumb_url=product.image,
                )
            )
    return query_answer


async def show_products_inline(subcategory_title: str, state: FSMContext, offset: int):
    start = offset
    end = offset + 25
    query_answer = []
    async with db.transaction():
        query = Product.load(parent=Subcategory).where(Subcategory.tg_name == subcategory_title)
        result = await query.gino.all()
    for product in result[start:end]:
        async with state.proxy() as state_data:
            state_data["product_info"] = {"is_liked": 0}
            keyboard = KeyboardGen(product=product, data=state_data)
            markup = keyboard.build_product_kb()
        query_answer.append(
            types.InlineQueryResultArticle(
                id=str(product.id),
                title=product.title,
                input_message_content=types.InputTextMessageContent(
                    message_text=f"<a href='{product.image}'>{product.title}</a>", parse_mode="HTML"
                ),
                reply_markup=markup,
                description=str(product.price) + "$",
                thumb_url=product.image,
            )
        )
    return query_answer


async def show_all_subcategory():
    subcategories = await Subcategory.query.gino.all()
    return subcategories


async def test():
    engine = await gino.create_engine(config.POSTGRES_URI)
    db.bind = engine
    result = await get_parent_child()
    for i in result:
        print(i.children)


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(test())
