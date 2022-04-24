from aiogram import types
from aiogram.dispatcher import FSMContext

from ..bot import bot, dispatcher
from ..utils import filters
from ..utils.database_models import SubChannel
from ..utils.state import AdminAddChannelState, AdminRemoveChannelState


def is_mention(message: types.Message) -> bool:
    return message.text and message.text.startswith("@")


@dispatcher.message_handler(
    lambda m: m.text == bot.phrases.admin.add_channel, filters.is_admin
)
async def add_channel_handler(message: types.Message):
    await AdminAddChannelState.waiting_channel_mention.set()
    await message.answer(bot.phrases.admin.enter_channel_mention)


@dispatcher.message_handler(
    is_mention, state=AdminAddChannelState.waiting_channel_mention
)
async def add_channel_mention_handler(message: types.Message, state: FSMContext):
    try:
        channel = await bot.get_chat(message.text)
    except Exception:
        return await message.answer(bot.phrases.admin.bot_is_not_a_member)

    async with state.proxy() as data:
        data["add_channel_mention"] = channel.mention
        data["add_channel_id"] = channel.id

    await AdminAddChannelState.waiting_channel_name.set()
    await message.answer(bot.phrases.admin.enter_channel_name)


@dispatcher.message_handler(state=AdminAddChannelState.waiting_channel_name)
async def add_channel_name_handler(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        channel_mention: str = data["add_channel_mention"]
        channel_id: int = data["add_channel_id"]

    await SubChannel.create(
        channel_id=channel_id,
        channel_mention=channel_mention,
        channel_button_text=message.text,
    )

    await state.finish()
    await message.answer(bot.phrases.admin.channel_added)


@dispatcher.message_handler(
    lambda m: m.text == bot.phrases.admin.remove_channel, filters.is_admin
)
async def remove_channel_handler(message: types.Message):
    await AdminRemoveChannelState.waiting_channel_mention.set()
    await message.answer(bot.phrases.admin.enter_channel_mention)


@dispatcher.message_handler(
    is_mention, state=AdminRemoveChannelState.waiting_channel_mention
)
async def remove_channel_mention_handler(message: types.Message, state: FSMContext):
    await SubChannel.filter(channel_mention=message.text).delete()
    await state.finish()
    await message.answer(bot.phrases.admin.channel_removed)
