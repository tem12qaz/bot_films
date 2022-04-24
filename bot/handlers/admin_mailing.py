from io import BytesIO
from pathlib import Path

from aiogram import types
from aiogram.dispatcher.storage import FSMContext
from bot.bot import bot, dispatcher
from bot.utils import filters, markups
from bot.utils.database_models import BotUser
from bot.utils.io import copy_buffer
from bot.utils.state import MailingState


@dispatcher.message_handler(
    lambda m: m.text == bot.phrases.mailing.cancel,
    filters.is_admin,
    state=[MailingState.waiting_button_name, MailingState.waiting_button_url],
)
async def add_button_cancel_handler(message: types.Message, state: FSMContext):
    await mailing_image_done(message, state)


@dispatcher.message_handler(
    lambda m: m.text == bot.phrases.mailing.cancel,
    filters.is_admin,
    state=MailingState.all_states,
)
async def mailing_cancel_handler(message: types.Message, state: FSMContext):
    await state.finish()
    await message.answer(bot.phrases.admin.admin, reply_markup=markups.admin_markup)


@dispatcher.message_handler(
    lambda m: m.text == bot.phrases.mailing.mailing, filters.is_admin
)
async def mailing_handler(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data["mailing_buttons"] = []

    await MailingState.waiting_message.set()
    await message.answer(
        bot.phrases.mailing.enter_mailing_text, reply_markup=markups.mailing_markup
    )


@dispatcher.message_handler(
    lambda m: m.text == bot.phrases.mailing.done, state=MailingState.waiting_message
)
async def mailing_text_done(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        if not data.get("mailing_text"):
            return

    await MailingState.waiting_image.set()
    await message.answer(bot.phrases.mailing.enter_image)


@dispatcher.message_handler(filters.is_admin, state=MailingState.waiting_message)
async def mailing_message_handler(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data["mailing_text"] = message.text

    await message.answer(bot.phrases.mailing.mailing_message_saved)


@dispatcher.message_handler(
    filters.is_admin,
    content_types=types.ContentType.PHOTO,
    state=MailingState.waiting_image,
)
async def mailing_image_handler(message: types.Message, state: FSMContext):
    buffer = BytesIO()
    photo = message.photo[-1]
    file = await photo.get_file()
    await photo.download(buffer)
    buffer.seek(0)

    filepath = Path(file.file_path)

    async with state.proxy() as data:
        data["mailing_image"] = {
            "buffer": buffer,
            "filename": filepath.name,
        }

    await message.answer(bot.phrases.mailing.mailing_image_saved)


@dispatcher.message_handler(
    lambda m: m.text == bot.phrases.mailing.done,
    filters.is_admin,
    state=MailingState.waiting_image,
)
async def mailing_image_done(message: types.Message, state: FSMContext):
    await MailingState.waiting_done.set()
    await message.answer(
        bot.phrases.mailing.make_mailing, reply_markup=markups.done_mailing_markup
    )


@dispatcher.message_handler(
    lambda m: m.text == bot.phrases.mailing.add_button,
    filters.is_admin,
    state=MailingState.waiting_done,
)
async def mailing_add_button_handler(message: types.Message, state: FSMContext):
    await MailingState.waiting_button_name.set()
    await message.answer(bot.phrases.mailing.enter_button_name)


@dispatcher.message_handler(filters.is_admin, state=MailingState.waiting_button_name)
async def mailing_button_name_handler(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data["mailing_button_name"] = message.text

    await MailingState.waiting_button_url.set()
    await message.answer(bot.phrases.mailing.enter_button_url)


@dispatcher.message_handler(
    lambda m: m.text.startswith("http"),
    filters.is_admin,
    state=MailingState.waiting_button_url,
)
async def mailing_button_url_handler(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        button_url = message.text
        button_name = data["mailing_button_name"]
        data["mailing_buttons"].append({"name": button_name, "url": button_url})

    await MailingState.waiting_done.set()
    await message.answer(bot.phrases.mailing.button_added)


@dispatcher.message_handler(
    lambda m: m.text == bot.phrases.mailing.done,
    filters.is_admin,
    state=MailingState.waiting_done,
)
async def mailing_done_handler(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        text: str = data.get("mailing_text")
        image: dict = data.get("mailing_image")
        buttons: list = data.get("mailing_buttons")

    markup = None if not buttons else types.InlineKeyboardMarkup(row_width=1)

    for button in buttons:
        markup.insert(types.InlineKeyboardButton(button["name"], url=button["url"]))

    sent_messages = 0
    bot_users = await BotUser.all()

    await state.finish()

    for bot_user in bot_users:
        file_input: types.InputFile = None

        if image is not None:
            image["buffer"].seek(0)
            file_input = types.InputFile(
                copy_buffer(image["buffer"]), image["filename"]
            )

        try:
            if file_input is None:
                await bot.send_message(bot_user.user_id, text, reply_markup=markup)
            else:
                await bot.send_photo(
                    bot_user.user_id, file_input, text, reply_markup=markup
                )
        except Exception:
            continue

        sent_messages += 1

    await message.answer(
        bot.phrases.mailing.mailing_done.format(sent_messages=sent_messages),
        reply_markup=markups.admin_markup,
    )
