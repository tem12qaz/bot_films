from aiogram import types

from bot.bot import bot


def is_admin(message: types.Message):
    return message.from_user and message.from_user.username == bot.config.admin_username
