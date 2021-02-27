from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from tgbot.keyboards.inline.callback_datas import create_callback
from tgbot.utils.db_api.quick_commands import get_parent_child, get_child_parent


async def category_keyboard():
    current_level = 0
    categories_qs = await get_parent_child()
    categories_markup = InlineKeyboardMarkup(row_width=1)
    for category in categories_qs:
        callback_data = await create_callback(level=current_level + 1, category_id=category.id)
        categories_markup.insert(InlineKeyboardButton(text=f"{category.tg_name}", callback_data=callback_data))
    return categories_markup


async def subcategory_keyboard(category_id: int):   # accepting category_id and getting data from db
    current_level = 1
    subcategories_qs = await get_child_parent(category_id=category_id)
    subcategories_markup = InlineKeyboardMarkup(row_width=1)
    for subcategory in subcategories_qs:
        callback_data = await create_callback(level=current_level + 1, category_id=category_id,
                                              subcategory_id=subcategory.id)
        subcategories_markup.insert(InlineKeyboardButton(text=f"{subcategory.tg_name}",
                                                         callback_data=callback_data))

    subcategories_markup.row(
        InlineKeyboardButton(text="◀ Назад",
                             callback_data=await create_callback(level=current_level - 1)))
    return subcategories_markup
