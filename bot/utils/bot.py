import asyncio
from typing import List

import aiogram
from aiogram.bot import Bot as BaseBot

from ..config import BotConfig
from ..phrases import BotPhrases


class Bot(BaseBot):
    def __init__(self, config: BotConfig, phrases: List[BotPhrases], *args, **kwargs):
        super().__init__(*args, token=config.bot_token, **kwargs)
        self.config = config
        self.all_phrases = phrases

    @property
    def phrases(self) -> BotPhrases:
        return self.all_phrases[0]

    async def request(self, *args, **kwargs):
        request_data = None

        while request_data is None:
            try:
                request_data = await super().request(*args, **kwargs)
            except aiogram.exceptions.RetryAfter as e:
                await asyncio.sleep(e.timeout)

        return request_data
