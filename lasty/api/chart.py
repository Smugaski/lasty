"""Chart API namespace — ``client.chart.*`` methods."""

from __future__ import annotations

from typing import AsyncIterator

from .base import BaseAPI
from ..models.common import PaginatedResponse, PaginationAttr
from ..models.artist import ArtistSummary
from ..models.tag import TopTag
from ..models.track import TopTrack

__all__ = ["ChartAPI"]


class ChartAPI(BaseAPI):
    """Global charts API methods.

    Access via ``client.chart``.
    """

    async def get_top_artists(
        self,
        *,
        limit: int | None = None,
        page: int | None = None,
    ) -> PaginatedResponse[ArtistSummary]:
        """Get the global top artists chart.

        Args:
            limit: Number of results per page.
            page: Page number to fetch.

        Returns:
            A paginated response containing `ArtistSummary`.
        """
        params = self._clean_params({"limit": limit, "page": page})
        data = await self._get("chart.getTopArtists", params)
        container = data.get("artists", {})
        artists = self._ensure_list(container.get("artist"))
        attr = container.get("@attr", {})
        return PaginatedResponse(
            items=[ArtistSummary.from_data(a) for a in artists],
            attr=PaginationAttr.from_data(attr),
        )

    async def iter_top_artists(
        self,
        *,
        limit: int | None = None,
        max_pages: int | None = None,
        max_items: int | None = None,
    ) -> AsyncIterator[ArtistSummary]:
        """Async iterator over global top artists chart, auto-paginating."""
        page = 1
        items_yielded = 0
        while True:
            if max_pages is not None and page > max_pages:
                break
            result = await self.get_top_artists(limit=limit, page=page)
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
        *,
        limit: int | None = None,
        page: int | None = None,
    ) -> PaginatedResponse[TopTag]:
        """Get the global top tags chart.

        Args:
            limit: Number of results per page.
            page: Page number to fetch.

        Returns:
            A paginated response containing `TopTag`.
        """
        params = self._clean_params({"limit": limit, "page": page})
        data = await self._get("chart.getTopTags", params)
        container = data.get("tags", {})
        tags = self._ensure_list(container.get("tag"))
        attr = container.get("@attr", {})
        return PaginatedResponse(
            items=[TopTag.from_data(t) for t in tags],
            attr=PaginationAttr.from_data(attr),
        )

    async def iter_top_tags(
        self,
        *,
        limit: int | None = None,
        max_pages: int | None = None,
        max_items: int | None = None,
    ) -> AsyncIterator[TopTag]:
        """Async iterator over global top tags chart, auto-paginating."""
        page = 1
        items_yielded = 0
        while True:
            if max_pages is not None and page > max_pages:
                break
            result = await self.get_top_tags(limit=limit, page=page)
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
        *,
        limit: int | None = None,
        page: int | None = None,
    ) -> PaginatedResponse[TopTrack]:
        """Get the global top tracks chart.

        Args:
            limit: Number of results per page.
            page: Page number to fetch.

        Returns:
            A paginated response containing `TopTrack`.
        """
        params = self._clean_params({"limit": limit, "page": page})
        data = await self._get("chart.getTopTracks", params)
        container = data.get("tracks", {})
        tracks = self._ensure_list(container.get("track"))
        attr = container.get("@attr", {})
        return PaginatedResponse(
            items=[TopTrack.from_data(t) for t in tracks],
            attr=PaginationAttr.from_data(attr),
        )

    async def iter_top_tracks(
        self,
        *,
        limit: int | None = None,
        max_pages: int | None = None,
        max_items: int | None = None,
    ) -> AsyncIterator[TopTrack]:
        """Async iterator over global top tracks chart, auto-paginating."""
        page = 1
        items_yielded = 0
        while True:
            if max_pages is not None and page > max_pages:
                break
            result = await self.get_top_tracks(limit=limit, page=page)
            for item in result.items:
                yield item
                items_yielded += 1
                if max_items is not None and items_yielded >= max_items:
                    return
            if page >= result.attr.total_pages or not result.items:
                break
            page += 1
