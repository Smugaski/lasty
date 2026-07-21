"""Geo API namespace — ``client.geo.*`` methods."""

from __future__ import annotations

from typing import AsyncIterator

from lasty.api.base import BaseAPI
from lasty.models.common import PaginatedResponse, PaginationAttr
from lasty.models.artist import ArtistSummary
from lasty.models.track import TopTrack

__all__ = ["GeoAPI"]


class GeoAPI(BaseAPI):
    """Geography-related API methods.

    Access via ``client.geo``.
    """

    async def get_top_artists(
        self,
        country: str,
        *,
        limit: int | None = None,
        page: int | None = None,
    ) -> PaginatedResponse[ArtistSummary]:
        """Get the most popular artists on Last.fm by country.

        Args:
            country: A country name (e.g. ``"Poland"``, ``"United Kingdom"``).
            limit: Number of results per page.
            page: Page number to fetch.

        Returns:
            A paginated response containing `ArtistSummary`.
        """
        params = self._clean_params(
            {
                "country": country,
                "limit": limit,
                "page": page,
            }
        )
        data = await self._get("geo.getTopArtists", params)
        container = data.get("topartists", {})
        artists = self._ensure_list(container.get("artist"))
        attr = container.get("@attr", {})
        return PaginatedResponse(
            items=[ArtistSummary.from_data(a) for a in artists],
            attr=PaginationAttr.from_data(attr),
        )

    async def iter_top_artists(
        self,
        country: str,
        *,
        limit: int | None = None,
        max_pages: int | None = None,
        max_items: int | None = None,
    ) -> AsyncIterator[ArtistSummary]:
        """Async iterator over country top artists, auto-paginating."""
        page = 1
        items_yielded = 0
        while True:
            if max_pages is not None and page > max_pages:
                break
            result = await self.get_top_artists(country, limit=limit, page=page)
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
        country: str,
        *,
        limit: int | None = None,
        page: int | None = None,
    ) -> PaginatedResponse[TopTrack]:
        """Get the most popular tracks on Last.fm by country.

        Args:
            country: A country name (e.g. ``"Germany"``).
            limit: Number of results per page.
            page: Page number to fetch.

        Returns:
            A paginated response containing `TopTrack`.
        """
        params = self._clean_params(
            {
                "country": country,
                "limit": limit,
                "page": page,
            }
        )
        data = await self._get("geo.getTopTracks", params)
        container = data.get("tracks", {})
        tracks = self._ensure_list(container.get("track"))
        attr = container.get("@attr", {})
        return PaginatedResponse(
            items=[TopTrack.from_data(t) for t in tracks],
            attr=PaginationAttr.from_data(attr),
        )

    async def iter_top_tracks(
        self,
        country: str,
        *,
        limit: int | None = None,
        max_pages: int | None = None,
        max_items: int | None = None,
    ) -> AsyncIterator[TopTrack]:
        """Async iterator over country top tracks, auto-paginating."""
        page = 1
        items_yielded = 0
        while True:
            if max_pages is not None and page > max_pages:
                break
            result = await self.get_top_tracks(country, limit=limit, page=page)
            for item in result.items:
                yield item
                items_yielded += 1
                if max_items is not None and items_yielded >= max_items:
                    return
            if page >= result.attr.total_pages or not result.items:
                break
            page += 1
