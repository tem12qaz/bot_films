from io import BytesIO

from aiogram import types

from ..bot import bot, dispatcher
from ..utils import filters
from ..utils.database_models import BotUser


@dispatcher.message_handler(
    lambda m: m.text == bot.phrases.admin.stats, filters.is_admin
)
async def stats_handler(message: types.Message):
    bot_users = await BotUser.all()
    buffer_data_str = "\n".join(map(lambda u: str(u.user_id), bot_users))
    buffer_data = buffer_data_str.encode(encoding="utf-8")
    buffer = BytesIO(buffer_data)
    input_file = types.InputFile(buffer, "users.txt")

    await message.answer_document(
        input_file,
        caption=bot.phrases.admin.stats_message.format(bot_users_count=len(bot_users)),
    )
