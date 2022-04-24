from typing import *

from pydantic import BaseModel, Field

from bot import root_path


class MailingPhrases(BaseModel):
    mailing: str = Field("Рассылка")
    cancel: str = Field("Отмена")
    done: str = Field("Готово")
    add_button: str = Field("Добавить кнопку")
    enter_mailing_text: str = Field("Введите сообщение рассылки")
    enter_image: str = Field("Укажите картинку")
    mailing_message_saved: str = Field("Сообщение сохранено")
    mailing_image_saved: str = Field("Картинка сохранена")
    make_mailing: str = Field("Разослать?")
    enter_button_name: str = Field("Введите название кнопки")
    enter_button_url: str = Field("Введите ссылку кнопки")
    button_added: str = Field("Кнопка добавлена")
    mailing_done: str = Field("Отправлено {sent_messages} сообщений")
    add_button: str = Field("Добавить кнопку")


class AdminPhrases(BaseModel):
    forward_post: str = Field("Перешлите пост из канала")
    admin: str = Field("Админка")
    add_channel: str = Field("Добавить канал")
    remove_channel: str = Field("Удалить канал")
    enter_channel_mention: str = Field("Введите @упоминание канала")
    enter_channel_name: str = Field(
        "Введите название канала (будет отображаться в кнопке)"
    )
    channel_added: str = Field("Канал добавлен")
    channel_removed: str = Field("Канал удален")

    bot_is_not_a_member: str = Field("Бот не находится в этом канале")

    add_film: str = Field("Добавить фильм")
    remove_film: str = Field("Удалить фильм")

    enter_film_name: str = Field("Введите название фильма")
    enter_film_code: str = Field("Введите код фильма")

    film_with_such_code_is_added: str = Field("Фильм с таким кодом уже добавлен")
    film_added: str = Field("Фильм добавлен")
    film_removed: str = Field("Фильм удален")

    enter_film_image: str = Field("Укажите картинку фильма")

    create_referral_link: str = Field("Создать реферальную ссылку")
    enter_username: str = Field("Укажите @юзернейм пользователя")
    user_not_found: str = Field("Пользователь не найден")
    referral_created: str = Field("Реферальная ссылка создана: {bot_user.referral_url}")
    referrals_data: str = Field("Рефералы")
    stats: str = Field("Статистика")
    stats_message: str = Field("В боте {bot_users_count} пользователей")


class BotPhrases(BaseModel):
    __lang_code__: str = None

    mailing: MailingPhrases = Field(MailingPhrases())

    referral_message: str = Field(
        "Вы пригласили {referral_data.referrals_count} человек"
    )
    bot_started: str = Field("Бот {bot.full_name} запущен")
    start_message: str = Field(
        """🥤 <b>Все фильмы из ТикТока</b>

Жми на кнопку чтобы узнать названия фильмов ⤵️"""
    )

    start_button_text: str = Field("🎥 НАЗВАНИЯ ФИЛЬМОВ 🎥")

    subscribe_message: str = Field(
        "<b>📝 Для использования бота, вы должны быть подписаны на наши каналы:</b>"
    )

    ive_subscribed: str = Field("🥤 Я ПОДПИСАЛСЯ 🥤")

    channel_button_fmt: str = Field("🎥 КАНАЛ {number}")
    havent_subscribed: str = Field("Вы не подписались на каналы")
    search_message: str = Field("🔎 Для поиска отправьте код фильма/сериала")

    film_message_fmt: str = Field(
        """🎥 Фильм №{film.code} называется: <b>{film.name}</b>
    
🔎 Для поиска отправьте код фильма/сериала"""
    )

    admin: AdminPhrases = Field(AdminPhrases())

    invalid_film_code: str = Field("Вы ввели неверный код фильма")

    unlocked_message: str = Field(
        """🤖Доступ открыт!

Отправь мне КОД и я пришлю тебе название!
--------------------
Все фильмы из ТикТока, есть в приватном канале⤵️"""
    )

    private_channel: str = Field("ПРИВАТНЫЙ КАНАЛ ↗️")

    @classmethod
    def load_all(cls) -> List["BotPhrases"]:
        phrases_dir = root_path / "phrases"
        parsed_phrases: List[BotPhrases] = []

        for phrases_path in phrases_dir.glob("*.json"):
            phrases = BotPhrases.parse_file(phrases_path)
            parsed_phrases.append(phrases)

        return parsed_phrases
