from io import BytesIO

from aiogram import types
from aiogram.dispatcher import FSMContext
from bot import root_path

from ..bot import bot, dispatcher
from ..utils import markups
from ..utils.database_models import BotUser, SubChannel
from ..utils.io import copy_buffer

assets_path = root_path / "assets"

with open(assets_path / "start_image.jpg", "rb") as f:
    start_image_buffer = BytesIO(f.read())


async def is_user_subscribed(user_id: int):
    sub_channels = await SubChannel.all()

    for sub_channel in sub_channels:
        try:
            member = await bot.get_chat_member(sub_channel.channel_id, user_id)
        except Exception:
            return False

        if member.status.lower() in ("kicked", "banned", "left"):
            return False

    return True


async def handle_referral(bot_user: BotUser, message: types.Message):
    try:
        args = message.get_args()
        referrer_user_id = int(args)
    except (ValueError, TypeError):
        return

    if bot_user.user_id == referrer_user_id:
        return

    referrer_bot_user = (
        await BotUser.filter(user_id=referrer_user_id)
        .prefetch_related("referral_data")
        .first()
    )

    if referrer_bot_user is None or not referrer_bot_user.referral_data:
        return

    referrer_bot_user.referral_data[0].referrals_count += 1
    await referrer_bot_user.referral_data[0].save()


@dispatcher.message_handler(commands=["start"], state="*")
async def start_handler(message: types.Message, state: FSMContext):
    await state.finish()
    input_file = types.InputFile(
        copy_buffer(start_image_buffer), filename=assets_path.name
    )

    bot_user, created = await BotUser.update_or_create(
        dict(username=message.from_user.username), user_id=message.from_user.id
    )

    await bot_user.fetch_related("referral_data")

    start_markup = markups.get_start_markup(message)

    if bot_user.referral_data:
        start_markup.row(
            types.InlineKeyboardButton(
                bot.phrases.admin.referrals_data, callback_data="referrals"
            ),
        )

    await message.answer_photo(
        input_file,
        caption=bot.phrases.start_message,
        reply_markup=start_markup,
    )

    if created:
        await handle_referral(bot_user, message)


@dispatcher.callback_query_handler(lambda q: q.data == markups.START_CB_DATA)
async def start_query_handler(query: types.CallbackQuery):
    await query.message.delete()
    await bot.send_message(
        query.from_user.id,
        bot.phrases.subscribe_message,
        reply_markup=await markups.get_subscribe_markup(),
    )


@dispatcher.callback_query_handler(lambda q: q.data == markups.SUB_CB_DATA)
async def sub_query_handler(query: types.CallbackQuery):
    if not await is_user_subscribed(query.from_user.id):
        return await query.answer(bot.phrases.havent_subscribed, show_alert=True)

    await query.message.delete()
    await bot.send_message(
        query.from_user.id,
        bot.phrases.unlocked_message,
        reply_markup=markups.unlocked_markup,
    )


@dispatcher.callback_query_handler(lambda q: q.data == "referrals")
async def referrals_query_handler(query: types.CallbackQuery):
    bot_user = (
        await BotUser.filter(user_id=query.from_user.id)
        .prefetch_related("referral_data")
        .first()
    )

    await bot.send_message(
        query.from_user.id,
        bot.phrases.referral_message.format(referral_data=bot_user.referral_data[0]),
    )
