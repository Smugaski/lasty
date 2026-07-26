"""The main Last.fm client entry point."""

from __future__ import annotations

import typing
from functools import cached_property
from typing import Self

from .http import HTTPClient
from .api.user import UserAPI
from .api.artist import ArtistAPI
from .api.album import AlbumAPI
from .api.track import TrackAPI
from .api.tag import TagAPI
from .api.chart import ChartAPI
from .api.geo import GeoAPI
from .api.library import LibraryAPI
from .api.auth import AuthAPI

__all__ = ["LastFM"]


class LastFM:
    """Async Last.fm API client.

    Acts as an entry point to the API namespaces (e.g. ``user``, ``artist``) and
    manages the underlying HTTP connection session using an async context manager.

    Example::

        async with LastFM(api_key="...", api_secret="...") as client:
            user_info = await client.user.get_info("rj")
            print(f"Playcount: {user_info.playcount}")

    Args:
        api_key: Your Last.fm API key.
        api_secret: Your Last.fm API secret (required for authenticated write calls).
        session_key: A user session key (sk) (required for user-specific authenticated write calls).
        user_agent: A custom User-Agent header (optional).
    """

    def __init__(
        self,
        api_key: str,
        api_secret: str | None = None,
        session_key: str | None = None,
        *,
        user_agent: str | None = None,
    ) -> None:
        self._http = HTTPClient(
            api_key=api_key,
            api_secret=api_secret,
            session_key=session_key,
            user_agent=user_agent,
        )

    async def __aenter__(self) -> Self:
        """Enter the async context manager, starting the HTTP session."""
        await self._http.start()
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: typing.Any,
    ) -> None:
        """Exit the async context manager, closing the HTTP session."""
        await self._http.close()

    @cached_property
    def user(self) -> UserAPI:
        """User API namespace."""
        return UserAPI(self._http)

    @cached_property
    def artist(self) -> ArtistAPI:
        """Artist API namespace."""
        return ArtistAPI(self._http)

    @cached_property
    def album(self) -> AlbumAPI:
        """Album API namespace."""
        return AlbumAPI(self._http)

    @cached_property
    def track(self) -> TrackAPI:
        """Track API namespace."""
        return TrackAPI(self._http)

    @cached_property
    def tag(self) -> TagAPI:
        """Tag API namespace."""
        return TagAPI(self._http)

    @cached_property
    def chart(self) -> ChartAPI:
        """Chart API namespace."""
        return ChartAPI(self._http)

    @cached_property
    def geo(self) -> GeoAPI:
        """Geo API namespace."""
        return GeoAPI(self._http)

    @cached_property
    def library(self) -> LibraryAPI:
        """Library API namespace."""
        return LibraryAPI(self._http)

    @cached_property
    def auth(self) -> AuthAPI:
        """Auth API namespace."""
        return AuthAPI(self._http)
