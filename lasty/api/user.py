"""User API namespace — ``client.user.*`` methods."""

from __future__ import annotations

from typing import AsyncIterator

from .base import BaseAPI
from ..enums import Period, TaggingType
from ..models.common import PaginatedResponse, PaginationAttr
from ..models.user import UserInfo, Friend
from ..models.track import (
    LovedTrack,
    RecentTrack,
    TopTrack,
    WeeklyChartTrack,
    BaseTrack,
)
from ..models.artist import TopArtist, WeeklyChartArtist, BaseArtist
from ..models.album import TopAlbum, WeeklyChartAlbum, BaseAlbum
from ..models.tag import UserTag
from ..models.chart import WeeklyChart, WeeklyChartAttr, ChartDateRange

__all__ = ["UserAPI"]


class UserAPI(BaseAPI):
    """User-related API methods.

    Access via ``client.user``.

    Example::

        async with LastFM(api_key="...") as client:
            user = await client.user.get_info("rj")
            print(user.name, user.playcount)
    """

    async def get_info(self, user: str) -> UserInfo:
        """Get information about a user profile.

        Args:
            user: The Last.fm username to look up.

        Returns:
            A `UserInfo` with the user's profile data.

        Raises:
            InvalidParametersError: If the user does not exist.
        """
        data = await self._get("user.getInfo", {"user": user})
        return UserInfo.from_data(data.get("user", {}))

    async def get_friends(
        self,
        user: str,
        *,
        recenttracks: bool = False,
        limit: int | None = None,
        page: int | None = None,
    ) -> PaginatedResponse[Friend]:
        """Get a list of the user's friends.

        Args:
            user: The Last.fm username.
            recenttracks: Include recent tracks for each friend.
            limit: Number of results per page (max 1000).
            page: Page number to fetch.

        Returns:
            A paginated list of `Friend` objects.
        """
        params = self._clean_params(
            {
                "user": user,
                "recenttracks": "1" if recenttracks else None,
                "limit": limit,
                "page": page,
            }
        )
        data = await self._get("user.getFriends", params)
        container = data.get("friends", {})
        friends_list = self._ensure_list(container.get("user"))
        attr = container.get("@attr", {})
        return PaginatedResponse(
            items=[Friend.from_data(f) for f in friends_list],
            attr=PaginationAttr.from_data(attr),
        )

    async def iter_friends(
        self,
        user: str,
        *,
        recenttracks: bool = False,
        limit: int | None = None,
        max_pages: int | None = None,
        max_items: int | None = None,
    ) -> AsyncIterator[Friend]:
        """Async iterator over all friends, auto-paginating.

        Args:
            user: The Last.fm username.
            recenttracks: Include recent tracks for each friend.
            limit: Number of results per page.

        Yields:
            `Friend` objects.
        """
        page = 1
        items_yielded = 0
        while True:
            if max_pages is not None and page > max_pages:
                break
            result = await self.get_friends(
                user,
                recenttracks=recenttracks,
                limit=limit,
                page=page,
            )
            for item in result.items:
                yield item
                items_yielded += 1
                if max_items is not None and items_yielded >= max_items:
                    return
            if page >= result.attr.total_pages or not result.items:
                break
            page += 1

    async def get_loved_tracks(
        self,
        user: str,
        *,
        limit: int | None = None,
        page: int | None = None,
    ) -> PaginatedResponse[LovedTrack]:
        """Get the user's loved tracks.

        Args:
            user: The Last.fm username.
            limit: Number of results per page (max 1000).
            page: Page number to fetch.

        Returns:
            A paginated list of `LovedTrack` objects.
        """
        params = self._clean_params(
            {
                "user": user,
                "limit": limit,
                "page": page,
            }
        )
        data = await self._get("user.getLovedTracks", params)
        container = data.get("lovedtracks", {})
        tracks_list = self._ensure_list(container.get("track"))
        attr = container.get("@attr", {})
        return PaginatedResponse(
            items=[LovedTrack.from_data(t) for t in tracks_list],
            attr=PaginationAttr.from_data(attr),
        )

    async def iter_loved_tracks(
        self,
        user: str,
        *,
        limit: int | None = None,
        max_pages: int | None = None,
        max_items: int | None = None,
    ) -> AsyncIterator[LovedTrack]:
        """Async iterator over all loved tracks, auto-paginating.

        Args:
            user: The Last.fm username.
            limit: Number of results per page.

        Yields:
            `LovedTrack` objects.
        """
        page = 1
        items_yielded = 0
        while True:
            if max_pages is not None and page > max_pages:
                break
            result = await self.get_loved_tracks(user, limit=limit, page=page)
            for item in result.items:
                yield item
                items_yielded += 1
                if max_items is not None and items_yielded >= max_items:
                    return
            if page >= result.attr.total_pages or not result.items:
                break
            page += 1

    async def get_recent_tracks(
        self,
        user: str,
        *,
        limit: int | None = None,
        page: int | None = None,
        from_ts: int | None = None,
        to_ts: int | None = None,
        extended: bool = False,
    ) -> PaginatedResponse[RecentTrack]:
        """Get a list of the user's recently scrobbled tracks.

        Args:
            user: The Last.fm username.
            limit: Number of results per page (max 200).
            page: Page number to fetch.
            from_ts: Start UNIX timestamp (inclusive).
            to_ts: End UNIX timestamp (inclusive).
            extended: If ``True``, include extended data (e.g. loved status).

        Returns:
            A paginated list of `RecentTrack` objects.
            If a track is currently playing, it will have ``now_playing=True``
            and ``date=None``.
        """
        params = self._clean_params(
            {
                "user": user,
                "limit": limit,
                "page": page,
                "from": from_ts,
                "to": to_ts,
                "extended": "1" if extended else None,
            }
        )
        data = await self._get("user.getRecentTracks", params)
        container = data.get("recenttracks", {})
        tracks_list = self._ensure_list(container.get("track"))
        attr = container.get("@attr", {})
        return PaginatedResponse(
            items=[RecentTrack.from_data(t) for t in tracks_list],
            attr=PaginationAttr.from_data(attr),
        )

    async def iter_recent_tracks(
        self,
        user: str,
        *,
        limit: int | None = None,
        from_ts: int | None = None,
        to_ts: int | None = None,
        extended: bool = False,
        max_pages: int | None = None,
        max_items: int | None = None,
    ) -> AsyncIterator[RecentTrack]:
        """Async iterator over recent tracks, auto-paginating.

        Args:
            user: The Last.fm username.
            limit: Number of results per page.
            from_ts: Start UNIX timestamp.
            to_ts: End UNIX timestamp.
            extended: Include extended data.

        Yields:
            `RecentTrack` objects.
        """
        page = 1
        items_yielded = 0
        while True:
            if max_pages is not None and page > max_pages:
                break
            result = await self.get_recent_tracks(
                user,
                limit=limit,
                page=page,
                from_ts=from_ts,
                to_ts=to_ts,
                extended=extended,
            )
            for item in result.items:
                yield item
                items_yielded += 1
                if max_items is not None and items_yielded >= max_items:
                    return
            if page >= result.attr.total_pages or not result.items:
                break
            page += 1

    async def get_top_albums(
        self,
        user: str,
        *,
        period: Period | str | None = None,
        limit: int | None = None,
        page: int | None = None,
    ) -> PaginatedResponse[TopAlbum]:
        """Get the user's top albums.

        Args:
            user: The Last.fm username.
            period: The time period (e.g. ``Period.SEVEN_DAY``).
            limit: Number of results per page (max 1000).
            page: Page number to fetch.

        Returns:
            A paginated list of `TopAlbum` objects.
        """
        params = self._clean_params(
            {
                "user": user,
                "period": period.value if isinstance(period, Period) else period,
                "limit": limit,
                "page": page,
            }
        )
        data = await self._get("user.getTopAlbums", params)
        container = data.get("topalbums", {})
        albums_list = self._ensure_list(container.get("album"))
        attr = container.get("@attr", {})
        return PaginatedResponse(
            items=[TopAlbum.from_data(a) for a in albums_list],
            attr=PaginationAttr.from_data(attr),
        )

    async def iter_top_albums(
        self,
        user: str,
        *,
        period: Period | str | None = None,
        limit: int | None = None,
        max_pages: int | None = None,
        max_items: int | None = None,
    ) -> AsyncIterator[TopAlbum]:
        """Async iterator over top albums, auto-paginating.

        Args:
            user: The Last.fm username.
            period: The time period.
            limit: Number of results per page.

        Yields:
            `TopAlbum` objects.
        """
        page = 1
        items_yielded = 0
        while True:
            if max_pages is not None and page > max_pages:
                break
            result = await self.get_top_albums(
                user, period=period, limit=limit, page=page
            )
            for item in result.items:
                yield item
                items_yielded += 1
                if max_items is not None and items_yielded >= max_items:
                    return
            if page >= result.attr.total_pages or not result.items:
                break
            page += 1

    async def get_top_artists(
        self,
        user: str,
        *,
        period: Period | str | None = None,
        limit: int | None = None,
        page: int | None = None,
    ) -> PaginatedResponse[TopArtist]:
        """Get the user's top artists.

        Args:
            user: The Last.fm username.
            period: The time period (e.g. ``Period.OVERALL``).
            limit: Number of results per page (max 1000).
            page: Page number to fetch.

        Returns:
            A paginated list of `TopArtist` objects.
        """
        params = self._clean_params(
            {
                "user": user,
                "period": period.value if isinstance(period, Period) else period,
                "limit": limit,
                "page": page,
            }
        )
        data = await self._get("user.getTopArtists", params)
        container = data.get("topartists", {})
        artists_list = self._ensure_list(container.get("artist"))
        attr = container.get("@attr", {})
        return PaginatedResponse(
            items=[TopArtist.from_data(a) for a in artists_list],
            attr=PaginationAttr.from_data(attr),
        )

    async def iter_top_artists(
        self,
        user: str,
        *,
        period: Period | str | None = None,
        limit: int | None = None,
        max_pages: int | None = None,
        max_items: int | None = None,
    ) -> AsyncIterator[TopArtist]:
        """Async iterator over top artists, auto-paginating.

        Args:
            user: The Last.fm username.
            period: The time period.
            limit: Number of results per page.

        Yields:
            `TopArtist` objects.
        """
        page = 1
        items_yielded = 0
        while True:
            if max_pages is not None and page > max_pages:
                break
            result = await self.get_top_artists(
                user, period=period, limit=limit, page=page
            )
            for item in result.items:
                yield item
                items_yielded += 1
                if max_items is not None and items_yielded >= max_items:
                    return
            if page >= result.attr.total_pages or not result.items:
                break
            page += 1

    async def get_top_tracks(
        self,
        user: str,
        *,
        period: Period | str | None = None,
        limit: int | None = None,
        page: int | None = None,
    ) -> PaginatedResponse[TopTrack]:
        """Get the user's top tracks.

        Args:
            user: The Last.fm username.
            period: The time period (e.g. ``Period.THREE_MONTH``).
            limit: Number of results per page (max 1000).
            page: Page number to fetch.

        Returns:
            A paginated list of `TopTrack` objects.
        """
        params = self._clean_params(
            {
                "user": user,
                "period": period.value if isinstance(period, Period) else period,
                "limit": limit,
                "page": page,
            }
        )
        data = await self._get("user.getTopTracks", params)
        container = data.get("toptracks", {})
        tracks_list = self._ensure_list(container.get("track"))
        attr = container.get("@attr", {})
        return PaginatedResponse(
            items=[TopTrack.from_data(t) for t in tracks_list],
            attr=PaginationAttr.from_data(attr),
        )

    async def iter_top_tracks(
        self,
        user: str,
        *,
        period: Period | str | None = None,
        limit: int | None = None,
        max_pages: int | None = None,
        max_items: int | None = None,
    ) -> AsyncIterator[TopTrack]:
        """Async iterator over top tracks, auto-paginating.

        Args:
            user: The Last.fm username.
            period: The time period.
            limit: Number of results per page.

        Yields:
            `TopTrack` objects.
        """
        page = 1
        items_yielded = 0
        while True:
            if max_pages is not None and page > max_pages:
                break
            result = await self.get_top_tracks(
                user, period=period, limit=limit, page=page
            )
            for item in result.items:
                yield item
                items_yielded += 1
                if max_items is not None and items_yielded >= max_items:
                    return
            if page >= result.attr.total_pages or not result.items:
                break
            page += 1

    async def get_top_tags(
        self,
        user: str,
        *,
        limit: int | None = None,
    ) -> list[UserTag]:
        """Get the user's top tags.

        Args:
            user: The Last.fm username.
            limit: Number of tags to return.

        Returns:
            A list of `UserTag` objects.
        """
        params = self._clean_params({"user": user, "limit": limit})
        data = await self._get("user.getTopTags", params)
        container = data.get("toptags", {})
        tags_list = self._ensure_list(container.get("tag"))
        return [UserTag.from_data(t) for t in tags_list]

    async def get_personal_tags(
        self,
        user: str,
        tag: str,
        taggingtype: TaggingType | str,
        *,
        limit: int | None = None,
        page: int | None = None,
    ) -> PaginatedResponse[BaseArtist | BaseAlbum | BaseTrack]:
        """Get the user's personal tags.

        Args:
            user: The Last.fm username.
            tag: The tag name.
            taggingtype: The type of tagged item (``"artist"``, ``"album"``, or ``"track"``).
            limit: Number of results per page.
            page: Page number to fetch.

        Returns:
            A paginated list of tagged items. The item type depends on
            ``taggingtype``.
        """
        tt = taggingtype.value if isinstance(taggingtype, TaggingType) else taggingtype
        params = self._clean_params(
            {
                "user": user,
                "tag": tag,
                "taggingtype": tt,
                "limit": limit,
                "page": page,
            }
        )
        data = await self._get("user.getPersonalTags", params)
        container = data.get("taggings", {})
        attr = container.get("@attr", {})

        items: list[BaseArtist | BaseAlbum | BaseTrack] = []
        if tt == "artist":
            artists_container = container.get("artists", {})
            for item_data in self._ensure_list(artists_container.get("artist")):
                items.append(BaseArtist.from_data(item_data))
        elif tt == "album":
            albums_container = container.get("albums", {})
            for item_data in self._ensure_list(albums_container.get("album")):
                items.append(BaseAlbum.from_data(item_data))
        elif tt == "track":
            tracks_container = container.get("tracks", {})
            for item_data in self._ensure_list(tracks_container.get("track")):
                items.append(BaseTrack.from_data(item_data))

        return PaginatedResponse(
            items=items,
            attr=PaginationAttr.from_data(attr),
        )

    async def get_weekly_album_chart(
        self,
        user: str,
        *,
        from_ts: int | None = None,
        to_ts: int | None = None,
        limit: int | None = None,
    ) -> WeeklyChart[WeeklyChartAlbum]:
        """Get the user's weekly album chart.

        Args:
            user: The Last.fm username.
            from_ts: Start UNIX timestamp. Must be used with ``to_ts``.
            to_ts: End UNIX timestamp. Must be used with ``from_ts``.
            limit: Maximum number of results (max 1000).

        Returns:
            A `WeeklyChart` of album entries.
        """
        params = self._clean_params(
            {
                "user": user,
                "from": from_ts,
                "to": to_ts,
                "limit": limit,
            }
        )
        data = await self._get("user.getWeeklyAlbumChart", params)
        container = data.get("weeklyalbumchart", {})
        albums_list = self._ensure_list(container.get("album"))
        attr = container.get("@attr", {})
        return WeeklyChart(
            items=[WeeklyChartAlbum.from_data(a) for a in albums_list],
            attr=WeeklyChartAttr.from_data(attr),
        )

    async def get_weekly_artist_chart(
        self,
        user: str,
        *,
        from_ts: int | None = None,
        to_ts: int | None = None,
        limit: int | None = None,
    ) -> WeeklyChart[WeeklyChartArtist]:
        """Get the user's weekly artist chart.

        Args:
            user: The Last.fm username.
            from_ts: Start UNIX timestamp. Must be used with ``to_ts``.
            to_ts: End UNIX timestamp. Must be used with ``from_ts``.
            limit: Maximum number of results (max 1000).

        Returns:
            A `WeeklyChart` of artist entries.
        """
        params = self._clean_params(
            {
                "user": user,
                "from": from_ts,
                "to": to_ts,
                "limit": limit,
            }
        )
        data = await self._get("user.getWeeklyArtistChart", params)
        container = data.get("weeklyartistchart", {})
        artists_list = self._ensure_list(container.get("artist"))
        attr = container.get("@attr", {})
        return WeeklyChart(
            items=[WeeklyChartArtist.from_data(a) for a in artists_list],
            attr=WeeklyChartAttr.from_data(attr),
        )

    async def get_weekly_track_chart(
        self,
        user: str,
        *,
        from_ts: int | None = None,
        to_ts: int | None = None,
        limit: int | None = None,
    ) -> WeeklyChart[WeeklyChartTrack]:
        """Get the user's weekly track chart.

        Args:
            user: The Last.fm username.
            from_ts: Start UNIX timestamp. Must be used with ``to_ts``.
            to_ts: End UNIX timestamp. Must be used with ``from_ts``.
            limit: Maximum number of results (max 1000).

        Returns:
            A `WeeklyChart` of track entries.
        """
        params = self._clean_params(
            {
                "user": user,
                "from": from_ts,
                "to": to_ts,
                "limit": limit,
            }
        )
        data = await self._get("user.getWeeklyTrackChart", params)
        container = data.get("weeklytrackchart", {})
        tracks_list = self._ensure_list(container.get("track"))
        attr = container.get("@attr", {})
        return WeeklyChart(
            items=[WeeklyChartTrack.from_data(t) for t in tracks_list],
            attr=WeeklyChartAttr.from_data(attr),
        )

    async def get_weekly_chart_list(self, user: str) -> list[ChartDateRange]:
        """Get a list of available weekly chart periods for a user.

        Args:
            user: The Last.fm username.

        Returns:
            A list of `ChartDateRange` objects representing
            available chart periods.
        """
        data = await self._get("user.getWeeklyChartList", {"user": user})
        container = data.get("weeklychartlist", {})
        charts_list = self._ensure_list(container.get("chart"))
        return [ChartDateRange.from_data(c) for c in charts_list]
