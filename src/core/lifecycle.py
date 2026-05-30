"""Application operational runtime event bindings managing startup and shutdown dependencies."""

import logging

from aiogram import Bot

logger = logging.getLogger(__name__)

__all__ = ("on_shutdown", "on_startup")


async def on_startup() -> None:
    """Execute asynchronous hooks needed when initializing components."""
    logger.info("Bot startup initiated. Binding components...")


async def on_shutdown(bot: Bot) -> None:
    """
    Gracefully terminate background routines and free persistent engine memory allocations.

    Parameters
    ----------
    bot : Bot
        The executing active instance of the Telegram Bot client.
    """
    logger.info("Termination protocol processed. Clearing active interface structures gracefully...")
    if bot.session:
        await bot.session.close()
