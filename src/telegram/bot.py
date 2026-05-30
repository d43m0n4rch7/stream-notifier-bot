"""Telegram structural interface factories mapping component initialization configurations safely."""

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from src.config.settings import settings

__all__ = ("create_bot", "create_dispatcher")


def create_bot() -> Bot:
    """
    Instantiate and compile global operational properties governing Telegram API clients.

    Returns
    -------
    Bot
        The finalized active bot engine instance.
    """
    return Bot(
        token=settings.bot_token.get_secret_value(),
        default=DefaultBotProperties(
            parse_mode=ParseMode.HTML,
            link_preview_is_disabled=True,
        ),
    )


def create_dispatcher() -> Dispatcher:
    """
    Construct unified application orchestration dispatchers mapping inbound events smoothly.

    Returns
    -------
    Dispatcher
        The unconfigured global update dispatcher context node.
    """
    return Dispatcher()
