from aiogram.dispatcher.filters.state import State, StatesGroup


class AdminAddChannelState(StatesGroup):
    waiting_channel_mention = State()
    waiting_channel_name = State()


class AdminRemoveChannelState(StatesGroup):
    waiting_channel_mention = State()


class AdminAddFilmState(StatesGroup):
    waiting_film_code = State()
    waiting_forwarded_post = State()


class AdminRemoveFilmState(StatesGroup):
    waiting_film_code = State()


class CreateReferralState(StatesGroup):
    waiting_username = State()


class MailingState(StatesGroup):
    waiting_message = State()
    waiting_image = State()
    waiting_done = State()
    waiting_button_name = State()
    waiting_button_url = State()
