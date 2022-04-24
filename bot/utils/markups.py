from aiogram import types
from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardMarkup,
)

from bot.bot import bot

from . import filters
from .database_models import SubChannel

START_CB_DATA = "start"
ADMIN_CB_DATA = "admin"
SUB_CB_DATA = "sub"

start_markup = InlineKeyboardMarkup()
start_markup.row(
    InlineKeyboardButton(bot.phrases.start_button_text, callback_data=START_CB_DATA)
)

start_admin_markup = InlineKeyboardMarkup()
start_admin_markup.row(
    InlineKeyboardButton(bot.phrases.start_button_text, callback_data=START_CB_DATA)
)
start_admin_markup.row(
    InlineKeyboardButton(bot.phrases.admin.admin, callback_data=ADMIN_CB_DATA)
)

admin_markup = ReplyKeyboardMarkup(resize_keyboard=True)
admin_markup.row(
    KeyboardButton(bot.phrases.admin.add_channel),
    KeyboardButton(bot.phrases.admin.remove_channel),
)
admin_markup.row(
    KeyboardButton(bot.phrases.admin.add_film),
    KeyboardButton(bot.phrases.admin.remove_film),
)
admin_markup.row(
    KeyboardButton(bot.phrases.admin.referrals_data),
    KeyboardButton(bot.phrases.admin.create_referral_link),
)
admin_markup.row(
    KeyboardButton(bot.phrases.admin.stats),
    KeyboardButton((bot.phrases.mailing.mailing)),
)

ive_subscribed = InlineKeyboardButton(
    bot.phrases.ive_subscribed, callback_data=SUB_CB_DATA
)

unlocked_markup = InlineKeyboardMarkup()
unlocked_markup.row(
    InlineKeyboardButton(
        bot.phrases.private_channel, url=bot.config.private_channel_join_url
    ),
)

mailing_markup = ReplyKeyboardMarkup(resize_keyboard=True)
mailing_markup.row(
    KeyboardButton(bot.phrases.mailing.done),
    KeyboardButton(bot.phrases.mailing.cancel),
)

done_mailing_markup = ReplyKeyboardMarkup(resize_keyboard=True)
done_mailing_markup.row(
    KeyboardButton(bot.phrases.mailing.done),
    KeyboardButton(bot.phrases.mailing.add_button),
    KeyboardButton(bot.phrases.mailing.cancel),
)


def get_start_markup(message: types.Message):
    if filters.is_admin(message):
        return start_admin_markup

    return start_markup


async def get_subscribe_markup() -> InlineKeyboardMarkup:
    sub_channels = await SubChannel.all()
    markup = InlineKeyboardMarkup()

    for sub_channel in sub_channels:
        markup.row(
            InlineKeyboardButton(
                sub_channel.channel_button_text,
                url=f"https://t.me/{sub_channel.channel_mention.strip('@')}",
            )
        )

    markup.row(ive_subscribed)
    return markup
