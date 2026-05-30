"""Runtime module setting up event runtimes and configuring high-performance selector engines."""

import asyncio
import contextlib
import logging
from contextlib import AsyncExitStack

from aiogram import F
from aiogram.methods import DeleteWebhook

from src.config.settings import settings
from src.core.lifecycle import on_shutdown, on_startup
from src.core.logging import setup_logging
from src.telegram.bot import create_bot, create_dispatcher
from src.telegram.notifier import TelegramTwitchNotifier
from src.twitch.client import TwitchAPI

logger = logging.getLogger(__name__)


async def main() -> None:
    """Initialize system tracking contexts and manage core dispatcher poller configurations."""
    setup_logging()

    bot = create_bot()
    dp = create_dispatcher()

    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)

    twitch_api = TwitchAPI(
        client_id=settings.twitch_client_id.get_secret_value(),
        client_secret=settings.twitch_secret.get_secret_value(),
    )

    async with AsyncExitStack() as stack:
        await stack.enter_async_context(twitch_api.client())

        notifier = TelegramTwitchNotifier(
            bot=bot,
            twitch_api=twitch_api,
            chat_id=settings.discussion_id,
            streamer_name=settings.streamer_username,
        )

        dp.message.register(
            notifier.handle_auto_comment,
            F.chat.id == settings.channel_id,
            F.is_automatic_forward
            | ((F.forward_from_chat.id == settings.channel_id) & F.forward_from_message_id.is_not_none()),
        )

        logger.info("All components bound. Monitoring operational feed stream for: %s", settings.streamer_username)

        await bot(DeleteWebhook(drop_pending_updates=True))

        polling_task = asyncio.create_task(notifier.start_polling())
        dp_task = asyncio.create_task(dp.start_polling(bot))  # pyright: ignore[reportUnknownMemberType]

        try:
            await asyncio.gather(polling_task, dp_task)
        finally:
            polling_task.cancel()
            dp_task.cancel()


if __name__ == "__main__":
    with contextlib.suppress(KeyboardInterrupt):
        asyncio.run(main())
