from io import BytesIO

from aiogram import types
from aiogram.dispatcher import FSMContext

from ..bot import bot, dispatcher
from ..utils import filters
from ..utils.database_models import BotUser, ReferralData
from ..utils.state import CreateReferralState


@dispatcher.message_handler(
    lambda m: m.text == bot.phrases.admin.create_referral_link, filters.is_admin
)
async def create_referral_link_handler(message: types.Message):
    await CreateReferralState.waiting_username.set()
    await message.answer(bot.phrases.admin.enter_username)


@dispatcher.message_handler(
    lambda m: m.text.startswith("@"), state=CreateReferralState.waiting_username
)
async def username_handler(message: types.Message, state: FSMContext):
    bot_user = await BotUser.get_or_none(username=message.text.strip("@"))
    await state.finish()

    if bot_user is None:
        return await message.answer(bot.phrases.admin.user_not_found)

    await ReferralData.update_or_create(bot_user=bot_user)
    await message.answer(bot.phrases.admin.referral_created.format(bot_user=bot_user))


@dispatcher.message_handler(
    lambda m: m.text == bot.phrases.admin.referrals_data, filters.is_admin
)
async def referrals_handler(message: types.Message):
    referral_data = await ReferralData.filter().prefetch_related("bot_user").all()
    buffer_data_str = "\n".join(
        f"@{r.bot_user.username} {r.referrals_count}" for r in referral_data
    )
    buffer_data = buffer_data_str.encode(encoding="utf-8")
    buffer = BytesIO(buffer_data)
    input_file = types.InputFile(buffer, "referrals.txt")
    await message.answer_document(input_file)
