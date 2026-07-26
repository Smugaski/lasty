"""Tag API namespace — ``client.tag.*`` methods."""

from __future__ import annotations

from typing import AsyncIterator

from .base import BaseAPI
from ..models.common import PaginatedResponse, PaginationAttr
from ..models.tag import TagInfo, Tag, TopTag
from ..models.album import TopAlbum
from ..models.artist import ArtistSummary
from ..models.track import TopTrack
from ..models.chart import ChartDateRange

__all__ = ["TagAPI"]


class TagAPI(BaseAPI):
    """Tag-related API methods.

    Access via ``client.tag``.
    """

    async def get_info(self, tag: str, *, lang: str | None = None) -> TagInfo:
        """Get metadata for a tag on Last.fm.

        Args:
            tag: The tag name to query.
            lang: ISO 639-1 language code for the biography/wiki.

        Returns:
            A `TagInfo` instance.
        """
        params = self._clean_params({"tag": tag, "lang": lang})
        data = await self._get("tag.getInfo", params)
        return TagInfo.from_data(data.get("tag", {}))

    async def get_similar(self, tag: str) -> list[Tag]:
        """Search for tags that are similar to this tag.

        Args:
            tag: The tag name to query.

        Returns:
            A list of similar `Tag` instances.
        """
        data = await self._get("tag.getSimilar", {"tag": tag})
        container = data.get("similartags", {})
        tags = self._ensure_list(container.get("tag"))
        return [Tag.from_data(t) for t in tags]

    async def get_top_albums(
        self,
        tag: str,
        *,
        limit: int | None = None,
        page: int | None = None,
    ) -> PaginatedResponse[TopAlbum]:
        """Get the top albums tagged with this tag.

        Args:
            tag: The tag name.
            limit: Number of results per page.
            page: Page number to fetch.

        Returns:
            A paginated response containing `TopAlbum`.
        """
        params = self._clean_params({"tag": tag, "limit": limit, "page": page})
        data = await self._get("tag.getTopAlbums", params)
        container = data.get("albums", {})
        albums = self._ensure_list(container.get("album"))
        attr = container.get("@attr", {})
        return PaginatedResponse(
            items=[TopAlbum.from_data(a) for a in albums],
            attr=PaginationAttr.from_data(attr),
        )

    async def iter_top_albums(
        self,
        tag: str,
        *,
        limit: int | None = None,
        max_pages: int | None = None,
        max_items: int | None = None,
    ) -> AsyncIterator[TopAlbum]:
        """Async iterator over top albums for a tag, auto-paginating."""
        page = 1
        items_yielded = 0
        while True:
            if max_pages is not None and page > max_pages:
                break
            result = await self.get_top_albums(tag, limit=limit, page=page)
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
        tag: str,
        *,
        limit: int | None = None,
        page: int | None = None,
    ) -> PaginatedResponse[ArtistSummary]:
        """Get the top artists tagged with this tag.

        Args:
            tag: The tag name.
            limit: Number of results per page.
            page: Page number to fetch.

        Returns:
            A paginated response containing `ArtistSummary`.
        """
        params = self._clean_params({"tag": tag, "limit": limit, "page": page})
        data = await self._get("tag.getTopArtists", params)
        container = data.get("topartists", {})
        artists = self._ensure_list(container.get("artist"))
        attr = container.get("@attr", {})
        return PaginatedResponse(
            items=[ArtistSummary.from_data(a) for a in artists],
            attr=PaginationAttr.from_data(attr),
        )

    async def iter_top_artists(
        self,
        tag: str,
        *,
        limit: int | None = None,
        max_pages: int | None = None,
        max_items: int | None = None,
    ) -> AsyncIterator[ArtistSummary]:
        """Async iterator over top artists for a tag, auto-paginating."""
        page = 1
        items_yielded = 0
        while True:
            if max_pages is not None and page > max_pages:
                break
            result = await self.get_top_artists(tag, limit=limit, page=page)
            for item in result.items:
                yield item
                items_yielded += 1
                if max_items is not None and items_yielded >= max_items:
                    return
            if page >= result.attr.total_pages or not result.items:
                break
            page += 1

    async def get_top_tags(self) -> list[TopTag]:
        """Get the top tags on Last.fm.

        Returns:
            A list of `TopTag` instances.
        """
        data = await self._get("tag.getTopTags")
        container = data.get("toptags", {})
        tags = self._ensure_list(container.get("tag"))
        return [TopTag.from_data(t) for t in tags]

    async def get_top_tracks(
        self,
        tag: str,
        *,
        limit: int | None = None,
        page: int | None = None,
    ) -> PaginatedResponse[TopTrack]:
        """Get the top tracks tagged with this tag.

        Args:
            tag: The tag name.
            limit: Number of results per page.
            page: Page number to fetch.

        Returns:
            A paginated response containing `TopTrack`.
        """
        params = self._clean_params({"tag": tag, "limit": limit, "page": page})
        data = await self._get("tag.getTopTracks", params)
        container = data.get("tracks", {})
        tracks = self._ensure_list(container.get("track"))
        attr = container.get("@attr", {})
        return PaginatedResponse(
            items=[TopTrack.from_data(t) for t in tracks],
            attr=PaginationAttr.from_data(attr),
        )

    async def iter_top_tracks(
        self,
        tag: str,
        *,
        limit: int | None = None,
        max_pages: int | None = None,
        max_items: int | None = None,
    ) -> AsyncIterator[TopTrack]:
        """Async iterator over top tracks for a tag, auto-paginating."""
        page = 1
        items_yielded = 0
        while True:
            if max_pages is not None and page > max_pages:
                break
            result = await self.get_top_tracks(tag, limit=limit, page=page)
            for item in result.items:
                yield item
                items_yielded += 1
                if max_items is not None and items_yielded >= max_items:
                    return
            if page >= result.attr.total_pages or not result.items:
                break
            page += 1

    async def get_weekly_chart_list(self, tag: str) -> list[ChartDateRange]:
        """Get a list of available weekly chart periods for this tag.

        Args:
            tag: The tag name.

        Returns:
            A list of `ChartDateRange` instances.
        """
        data = await self._get("tag.getWeeklyChartList", {"tag": tag})
        container = data.get("weeklychartlist", {})
        charts = self._ensure_list(container.get("chart"))
        return [ChartDateRange.from_data(c) for c in charts]
