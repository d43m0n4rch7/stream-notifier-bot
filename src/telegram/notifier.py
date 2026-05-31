"""Orchestration service layer analyzing tracking patterns and broadcasting channel updates state shifts."""

import asyncio
import logging
import time
from collections import deque
from dataclasses import dataclass
from typing import Final

from aiogram import Bot, html
from aiogram.exceptions import TelegramAPIError
from aiogram.types import BufferedInputFile, InputMediaPhoto, Message

from src.config.settings import settings
from src.services.localization import LocalizationManager
from src.telegram.keyboards import get_auto_comment_keyboard, get_offline_keyboard, get_online_keyboard
from src.twitch.client import TwitchAPI
from src.twitch.models import StreamInfo

logger = logging.getLogger(__name__)

__all__ = ("TelegramTwitchNotifier",)


@dataclass
class ActiveMessage:
    """Record instance mapping specific sent notification tracking coordinates."""

    message_id: int
    chat_id: int
    expires_at: float | None = None


class TelegramTwitchNotifier:
    """Core tracking service managing notification intervals and automated group comment logic."""

    OFFLINE_GRACE_PERIOD: Final[int] = 300
    DELETE_AFTER_OFFLINE: Final[int] = 28800

    def __init__(self, bot: Bot, twitch_api: TwitchAPI, chat_id: int, streamer_name: str) -> None:
        """
        Initialize the coordination service with necessary api client layers.

        Parameters
        ----------
        bot : Bot
            Authorized active aiogram execution interface endpoint.
        twitch_api : TwitchAPI
            Client backend managing connectivity with external media telemetry streams.
        chat_id : int
            Target community channel chat numerical identification index.
        streamer_name : str
            Broadcaster identity monitor target key profile entry name.
        """
        self.bot = bot
        self.twitch_api = twitch_api
        self.chat_id = chat_id
        self.streamer_name = streamer_name

        self.is_live: bool = False
        self.active_messages: dict[int, ActiveMessage] = {}
        self._processed_posts: deque[int] = deque(maxlen=2000)
        self.i18n = LocalizationManager(settings.LOCALES_PATH)

    async def handle_auto_comment(self, message: Message) -> None:
        """
        Intercept inbound feed movements and append corresponding navigation hints automatically.

        Parameters
        ----------
        message : Message
            The message update context dispatched via aiogram event monitoring layers.
        """
        if message.message_id in self._processed_posts:
            return

        if message.forward_from_message_id in self.active_messages:
            logger.info("Ignoring auto-forward loop routing for active notification ID: %s", message.message_id)
            return

        self._processed_posts.append(message.message_id)

        try:
            keyboard = get_auto_comment_keyboard(settings.channel_chat_link, self.i18n)
            await message.reply(
                text=self.i18n.t("notifications.auto_comment.text"),
                reply_markup=keyboard,
            )
            logger.info("Auto-forward feed verification reply processed on message ID: %s", message.message_id)
        except TelegramAPIError:
            logger.exception("Failed execution delivery handling automated chat entry feedback.")

    async def start_polling(self) -> None:
        """Launch endless asynchronous loop monitoring remote track changes regularly."""
        logger.info("Initializing background state telemetry processor for target: %s", self.streamer_name)

        async with asyncio.TaskGroup() as tg:
            tg.create_task(self._cleanup_loop())

            while True:
                # noinspection PyBroadException
                try:
                    stream_info = await self.twitch_api.get_stream_status(self.streamer_name)

                    if stream_info and not self.is_live:
                        logger.info("Broadcasting state delta recognized: Stream target live.")
                        self.is_live = True
                        tg.create_task(self._on_stream_online(stream_info))
                    elif not stream_info and self.is_live:
                        logger.info("Broadcasting state delta recognized: Stream offline. Initializing countdown delay.")
                        self.is_live = False
                        tg.create_task(self._on_stream_offline())
                except Exception:
                    logger.exception("Uncaught anomaly within stream operational check cycle.")

                await asyncio.sleep(60)

    async def _on_stream_online(self, stream_info: StreamInfo) -> None:
        """
        Construct visual elements and broadcast a new active notification card down to target.

        Parameters
        ----------
        stream_info : StreamInfo
            The current verified state payload tracking stream context values.
        """
        user_info = await self.twitch_api.get_user_info(self.streamer_name)
        if not user_info:
            return

        kb = get_online_keyboard(self.streamer_name)
        caption = self.i18n.t(
            "notifications.online.caption",
            stream_title=html.quote(stream_info.title or "No Title"),
            game_name=html.quote(stream_info.game_name or "Unknown Game"),
        )

        img_url = f"{stream_info.thumbnail_url.replace('{width}', '1280').replace('{height}', '720')}?t={int(time.time())}"
        photo_to_send: BufferedInputFile | str = img_url

        if bytes_data := await self.twitch_api.download_thumbnail(img_url):
            photo_to_send = BufferedInputFile(bytes_data, filename="thumbnail.jpg")

        try:
            msg = await self.bot.send_photo(chat_id=self.chat_id, photo=photo_to_send, caption=caption, reply_markup=kb)
            self.active_messages[msg.message_id] = ActiveMessage(message_id=msg.message_id, chat_id=self.chat_id)
        except TelegramAPIError:
            logger.exception("Failed delivering live network status notice broadcast profile.")

    async def _on_stream_offline(self) -> None:
        """Trigger countdown sequences verifying disconnect validity before flipping card records offline."""
        await asyncio.sleep(self.OFFLINE_GRACE_PERIOD)
        if self.is_live:
            logger.info("Broadcaster connectivity re-assertion monitored. Disabling graceful sequence.")
            return

        user_info = await self.twitch_api.get_user_info(self.streamer_name)
        if not user_info:
            return

        latest_vod = await self.twitch_api.get_latest_vod(user_info.id)
        offline_img = user_info.offline_image_url or user_info.profile_image_url
        expiration_time = time.time() + self.DELETE_AFTER_OFFLINE

        kb = get_offline_keyboard(latest_vod.url if latest_vod else "", self.i18n)
        caption = self.i18n.t("notifications.offline.caption")

        for msg_id, active_msg in self.active_messages.items():
            if active_msg.expires_at is None:
                active_msg.expires_at = expiration_time
                try:
                    await self.bot.edit_message_media(
                        media=InputMediaPhoto(media=str(offline_img), caption=caption),
                        chat_id=active_msg.chat_id,
                        message_id=msg_id,
                        reply_markup=kb,
                    )
                except TelegramAPIError:
                    logger.exception("Failed executing inline message transition updates node ID: %s", msg_id)

    async def _cleanup_loop(self) -> None:
        """Background routine evaluating expiration timings and wiping aged notification history blocks."""
        while True:
            # noinspection PyBroadException
            try:
                current_time = time.time()
                expired_ids = [
                    msg_id
                    for msg_id, active_msg in self.active_messages.items()
                    if active_msg.expires_at is not None and current_time >= active_msg.expires_at
                ]

                for msg_id in expired_ids:
                    active_msg = self.active_messages.pop(msg_id)
                    try:
                        await self.bot.delete_message(chat_id=active_msg.chat_id, message_id=msg_id)
                        logger.info("Executed message asset degradation: Cleared broadcast tracking block ID: %s", msg_id)
                    except TelegramAPIError:
                        logger.exception("Error clearing node tracking reference message ID: %s", msg_id)

            except Exception:
                logger.exception("Background worker encountered error scrubbing internal transaction history.")

            await asyncio.sleep(300)
