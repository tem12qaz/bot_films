from io import BytesIO

from aiogram import types

from ..bot import bot, dispatcher
from ..utils import markups
from ..utils.database_models import Film
from .admin_films import is_film_code
from .start import is_user_subscribed


@dispatcher.message_handler(is_film_code, state=None)
async def film_message_handler(message: types.Message):
    if not await is_user_subscribed(message.from_user.id):
        return await message.answer(
            bot.phrases.subscribe_message,
            reply_markup=await markups.get_subscribe_markup(),
        )

    film_code = int(message.text)
    film = await Film.get_or_none(code=film_code)

    if film is None:
        return await message.answer(bot.phrases.invalid_film_code)

    await bot.forward_message(message.from_user.id, film.chat_id, film.message_id)

    # buffer = BytesIO(film.image_bytes)
    # input_file = types.InputFile(buffer)

    # await message.answer_photo(input_file, caption=film.name)
