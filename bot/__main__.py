import argparse
import logging
import os

from aiogram import executor
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from tortoise import Tortoise

from . import root_path
from .bot import bot, dispatcher

handlers_path = root_path / "bot" / "handlers"


class ArgsNamespace(argparse.Namespace):
    handler: str
    jump: bool


def parse_args() -> ArgsNamespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--handler", help="Name of a handler file to create")
    parser.add_argument(
        "--jump", action="store_true", help="Whether to jump to the new created handler"
    )
    return parser.parse_args()


def create_handler(name: str):
    HANDLER_CODE = """from aiogram import types
from ..bot import dispatcher, bot
"""

    handler_path = handlers_path / f"{name.lower()}.py"
    handler_path.write_text(HANDLER_CODE, "utf-8")
    return handler_path


def load_handlers():
    for filepath in handlers_path.glob("*.py"):
        __import__(f"bot.handlers.{filepath.stem}")


def main():
    args = parse_args()

    if args.handler:
        handler_path = create_handler(args.handler)

        if args.jump:
            os.system(f"code {handler_path.absolute()}")

        return

    log_filename = str((root_path / "logs.log").resolve())

    logging.basicConfig(
        filename=log_filename,
        level=logging.ERROR,
        format=r"%(asctime)s %(levelname)s %(funcName)s(%(lineno)d) %(message)s",
    )

    logger = logging.getLogger("bot")
    dispatcher.middleware.setup(LoggingMiddleware(logger=logger))

    load_handlers()

    async def on_startup(*_):
        await Tortoise.init(
            modules={"models": ["bot.utils.database_models"]},
            db_url=f"sqlite://{root_path / 'database.sqlite3'}",
        )

        await Tortoise.generate_schemas()

        me = await bot.get_me()
        print(bot.phrases.bot_started.format(bot=me))

    async def on_shutdown(*_):
        await Tortoise.close_connections()

    executor.start_polling(
        dispatcher,
        skip_updates=False,
        loop=bot.loop,
        on_startup=on_startup,
        on_shutdown=on_shutdown,
    )


main()
