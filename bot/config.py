from pydantic import BaseModel, Field

from bot import root_path


class BotConfig(BaseModel):
    __config_filenames__ = ("config_dev.json", "config.json")

    bot_token: str = Field("API токен из @BotFather")
    admin_username: str = Field("Username администратора бота")
    private_channel_join_url: str = Field("https://t.me/")

    @classmethod
    def load_first(cls):
        for filename in cls.__config_filenames__:
            path = root_path / filename

            if path.exists():
                return cls.parse_file(path)
