"""Asynchronous Twitch integration layer handling authentication workflows and pipeline operations."""

import asyncio
import logging
import time
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from http import HTTPStatus
from typing import Any, cast

import aiohttp

from src.twitch.models import StreamInfo, UserInfo, VodInfo

logger = logging.getLogger(__name__)

__all__ = ("TwitchAPI",)

type JSONDict = dict[str, Any]


class TwitchAPI:
    """Client backend interfacing with Twitch API components securely."""

    def __init__(self, client_id: str, client_secret: str) -> None:
        """
        Initialize core identifiers needed for internal state caching.

        Parameters
        ----------
        client_id : str
            Client identifier key provided by Twitch Developer Console.
        client_secret : str
            Secret authorization string matching the client app validation.
        """
        self.client_id = client_id
        self.client_secret = client_secret

        self.access_token: str | None = None
        self.token_expires_at: float = 0
        self.session: aiohttp.ClientSession | None = None
        self._token_lock = asyncio.Lock()

    @asynccontextmanager
    async def client(self) -> AsyncGenerator[aiohttp.ClientSession, None]:
        """
        Context manager constructing and dismantling persistent web protocol connection pooling.

        Yields
        ------
        aiohttp.ClientSession
            The active network connectivity pool context.
        """
        session = aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=30))
        self.session = session
        try:
            yield session
        finally:
            await session.close()

    async def _refresh_access_token(self, session: aiohttp.ClientSession) -> str | None:
        """
        Verify validity of internal credentials and pull missing tokens when matching lifespan bounds.

        Parameters
        ----------
        session : aiohttp.ClientSession
            Active transport layer session handling external requests.

        Returns
        -------
        str | None
            A verified bearer credential token if authorization resolves successfully.
        """
        async with self._token_lock:
            if self.access_token and time.time() < (self.token_expires_at - 300):
                return self.access_token

            url = "https://id.twitch.tv/oauth2/token"
            params = {
                "client_id": self.client_id,
                "client_secret": self.client_secret,
                "grant_type": "client_credentials",
            }

            async with session.post(url, params=params) as resp:
                resp.raise_for_status()
                data: JSONDict = await resp.json()
                self.access_token = data["access_token"]
                self.token_expires_at = time.time() + data.get("expires_in", 3600)
                logger.info("Successfully refreshed Twitch upstream access token.")
                return self.access_token

    async def _make_request(
        self, endpoint: str, params: JSONDict | None = None, *, _is_retry: bool = False
    ) -> JSONDict | None:
        """
        Dispatch uniform queries toward target platform endpoint bindings securely.

        Parameters
        ----------
        endpoint : str
            Relative remote routing target pattern appended to baseline URL.
        params : JSONDict | None, optional
            Variable payload mappings passed during retrieval, by default None.
        _is_retry : bool, optional
            Internal tracking flag monitoring token fallback verification loop, by default False.

        Returns
        -------
        JSONDict | None
            Parsed structured collection dict when operation resolves with valid payloads.
        """
        if not self.session or self.session.closed:
            error_msg = "TwitchAPI requests require an active, managed underlying network context session."
            raise RuntimeError(error_msg)

        try:
            token = await self._refresh_access_token(self.session)
            headers = {
                "Client-ID": self.client_id,
                "Authorization": f"Bearer {token}",
            }
            url = f"https://api.twitch.tv/helix/{endpoint}"

            async with self.session.get(url, headers=headers, params=params) as resp:
                if resp.status == HTTPStatus.UNAUTHORIZED and not _is_retry:
                    logger.warning("Twitch OAuth token verification failed. Re-authenticating...")
                    self.access_token = None
                    return await self._make_request(endpoint, params, _is_retry=True)

                if resp.status == HTTPStatus.OK:
                    return cast("JSONDict", await resp.json())

                logger.error("Twitch API communication error: HTTP %s.", resp.status)
                return None
        except aiohttp.ClientError:
            logger.exception("Upstream target layer failure executing Twitch request.")
            return None

    async def get_stream_status(self, username: str) -> StreamInfo | None:
        """
        Fetch targeted operational session trace info matching specified profile handle name.

        Parameters
        ----------
        username : str
            Target login handle associated with user verification.

        Returns
        -------
        StreamInfo | None
            Live telemetry data collection record if broadcaster is actively online.
        """
        data = await self._make_request(endpoint="streams", params={"user_login": username})
        if data and (streams := data.get("data")) and isinstance(streams, list) and streams:
            return StreamInfo.model_validate(streams[0])
        return None

    async def get_user_info(self, username: str) -> UserInfo | None:
        """
        Acquire generic user tracking definitions from the target registry pipeline.

        Parameters
        ----------
        username : str
            Target system login username handle identity.

        Returns
        -------
        UserInfo | None
            A valid identity profile structure if record matching completes.
        """
        data = await self._make_request(endpoint="users", params={"login": username})
        if data and (users := data.get("data")) and isinstance(users, list) and users:
            return UserInfo.model_validate(users[0])
        return None

    async def get_latest_vod(self, user_id: str) -> VodInfo | None:
        """
        Locate the most recent recorded archival stream event stored within the profile video log.

        Parameters
        ----------
        user_id : str
            Unique numeric or system persistent database identifier string.

        Returns
        -------
        VodInfo | None
            Parsed file tracking schema defining matching media context logs.
        """
        data = await self._make_request(endpoint="videos", params={"user_id": user_id, "type": "archive", "first": 1})
        if data and (videos := data.get("data")) and isinstance(videos, list) and videos:
            return VodInfo.model_validate(videos[0])
        return None

    async def download_thumbnail(self, url: str) -> bytes | None:
        """
        Pull raw stream media byte contents for localization payload transfer operations.

        Parameters
        ----------
        url : str
            Target file path location resolving over active network pipelines.

        Returns
        -------
        bytes | None
            Raw unencoded text or file byte sequences if operation terminates smoothly.
        """
        if not self.session or self.session.closed:
            return None
        try:
            async with self.session.get(url) as response:
                if response.status == HTTPStatus.OK:
                    return await response.read()
                logger.warning("Twitch CDN call returned anomalous status: %s", response.status)
        except aiohttp.ClientError:
            logger.exception("Fatal processing download call targeting stream thumbnail.")
        return None
