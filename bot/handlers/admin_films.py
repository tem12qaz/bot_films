from io import BytesIO

from aiogram import types
from aiogram.dispatcher import FSMContext
from tortoise import exceptions as tortoise_exceptions

from ..bot import bot, dispatcher
from ..utils import filters
from ..utils.database_models import Film
from ..utils.state import AdminAddFilmState, AdminRemoveFilmState


def is_film_code(message: types.Message) -> bool:
    return message.text and message.text.isdigit()


@dispatcher.message_handler(
    lambda m: m.text == bot.phrases.admin.add_film, filters.is_admin
)
async def add_film_handler(message: types.Message):
    await AdminAddFilmState.waiting_film_code.set()
    await message.answer(bot.phrases.admin.enter_film_code)


@dispatcher.message_handler(is_film_code, state=AdminAddFilmState.waiting_film_code)
async def film_code_handler(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data["add_film_code"] = int(message.text)

    await AdminAddFilmState.waiting_forwarded_post.set()
    await message.answer(bot.phrases.admin.forward_post)


@dispatcher.message_handler(
    lambda m: m.forward_from_chat is not None and m.forward_from_message_id is not None,
    state=AdminAddFilmState.waiting_forwarded_post,
    content_types=types.ContentTypes.ANY,
)
async def film_post_handler(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        film_code: int = data["add_film_code"]

    await state.finish()

    try:
        await Film.create(
            code=film_code,
            chat_id=message.forward_from_chat.id,
            message_id=message.forward_from_message_id,
        )
    except tortoise_exceptions.IntegrityError:
        return await message.answer(bot.phrases.admin.film_with_such_code_is_added)

    await message.answer(bot.phrases.admin.film_added)


@dispatcher.message_handler(
    lambda m: m.text == bot.phrases.admin.remove_film, filters.is_admin
)
async def remove_film_handler(message: types.Message):
    await AdminRemoveFilmState.waiting_film_code.set()
    await message.answer(bot.phrases.admin.enter_film_code)


@dispatcher.message_handler(is_film_code, state=AdminRemoveFilmState.waiting_film_code)
async def remove_film_code_handler(message: types.Message, state: FSMContext):
    await Film.filter(code=int(message.text)).delete()
    await state.finish()
    await message.answer(bot.phrases.admin.film_removed)
