from aiogram import types

from ..bot import bot, dispatcher
from ..utils import filters, markups


@dispatcher.callback_query_handler(
    lambda q: q.data == markups.ADMIN_CB_DATA, filters.is_admin
)
async def admin_callback_query(query: types.CallbackQuery):
    await bot.send_message(
        query.from_user.id, bot.phrases.admin.admin, reply_markup=markups.admin_markup
    )
