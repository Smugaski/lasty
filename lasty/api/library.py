"""Library API namespace — ``client.library.*`` methods."""

from __future__ import annotations

from typing import AsyncIterator

from .base import BaseAPI
from ..models.common import PaginatedResponse, PaginationAttr
from ..models.artist import LibraryArtist

__all__ = ["LibraryAPI"]


class LibraryAPI(BaseAPI):
    """User library API methods.

    Access via ``client.library``.
    """

    async def get_artists(
        self,
        user: str,
        *,
        limit: int | None = None,
        page: int | None = None,
    ) -> PaginatedResponse[LibraryArtist]:
        """Get a list of the artists in a user's library.

        Args:
            user: The Last.fm username.
            limit: Number of results per page.
            page: Page number to fetch.

        Returns:
            A paginated response containing `LibraryArtist`.
        """
        params = self._clean_params(
            {
                "user": user,
                "limit": limit,
                "page": page,
            }
        )
        data = await self._get("library.getArtists", params)
        container = data.get("artists", {})
        artists = self._ensure_list(container.get("artist"))
        attr = container.get("@attr", {})
        return PaginatedResponse(
            items=[LibraryArtist.from_data(a) for a in artists],
            attr=PaginationAttr.from_data(attr),
        )

    async def iter_artists(
        self,
        user: str,
        *,
        limit: int | None = None,
        max_pages: int | None = None,
        max_items: int | None = None,
    ) -> AsyncIterator[LibraryArtist]:
        """Async iterator over artists in library, auto-paginating."""
        page = 1
        items_yielded = 0
        while True:
            if max_pages is not None and page > max_pages:
                break
            result = await self.get_artists(user, limit=limit, page=page)
            for item in result.items:
                yield item
                items_yielded += 1
                if max_items is not None and items_yielded >= max_items:
                    return
            if page >= result.attr.total_pages or not result.items:
                break
            page += 1
