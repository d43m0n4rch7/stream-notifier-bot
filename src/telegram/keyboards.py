"""Layout compilation module mapping functional interactive message command buttons."""

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from src.services.localization import LocalizationManager

__all__ = ("get_auto_comment_keyboard", "get_offline_keyboard", "get_online_keyboard")


def get_auto_comment_keyboard(chat_link: str, i18n: LocalizationManager) -> InlineKeyboardMarkup:
    """
    Build standardized single-button matrices routing conversations toward associated forum streams.

    Parameters
    ----------
    chat_link : str
        Target hypermedia path endpoint routing active discussion feeds.
    i18n : LocalizationManager
        The executing localization engine layout system reference.

    Returns
    -------
    InlineKeyboardMarkup
        The compiled inline user interface control element.
    """
    return InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text=i18n.t("notifications.buttons.link"), url=chat_link)]]
    )


def get_online_keyboard(streamer_name: str) -> InlineKeyboardMarkup:
    """
    Assemble active streaming tracking reference points redirecting toward distribution nodes.

    Parameters
    ----------
    streamer_name : str
        The unique username identifier tracking the channel platform profiles.

    Returns
    -------
    InlineKeyboardMarkup
        The constructed multi-button target action row.
    """
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="Twitch", url=f"https://twitch.tv/{streamer_name}"),
                InlineKeyboardButton(text="VK Live", url=f"https://live.vkvideo.ru/{streamer_name}"),
            ]
        ]
    )


def get_offline_keyboard(vod_url: str, i18n: LocalizationManager) -> InlineKeyboardMarkup | None:
    """
    Generate reference point connections routing toward stored historical video archives.

    Parameters
    ----------
    vod_url : str
        Target redirection routing path linking towards the recorded broadcast archive.
    i18n : LocalizationManager
        The executing localization engine layout system reference.

    Returns
    -------
    InlineKeyboardMarkup | None
        The functional button interface layout structure, or None if no link exists.
    """
    if not vod_url:
        return None
    return InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text=i18n.t("notifications.buttons.watch_vod"), url=vod_url)]]
    )
