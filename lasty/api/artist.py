"""Artist API namespace — ``client.artist.*`` methods."""

from __future__ import annotations

from typing import AsyncIterator

from .base import BaseAPI
from ..models.common import PaginatedResponse, PaginationAttr
from ..models.artist import (
    ArtistInfo,
    ArtistCorrection,
    SimilarArtist,
    TopArtist,
)
from ..models.album import TopAlbum
from ..models.track import TopTrack
from ..models.tag import Tag, TopTag

__all__ = ["ArtistAPI"]


class ArtistAPI(BaseAPI):
    """Artist-related API methods.

    Access via ``client.artist``.
    """

    async def get_info(
        self,
        artist: str,
        *,
        mbid: str | None = None,
        autocorrect: bool = False,
        username: str | None = None,
        lang: str | None = None,
    ) -> ArtistInfo:
        """Get the metadata for an artist.

        Args:
            artist: The artist name to query.
            mbid: The MusicBrainz ID for the artist.
            autocorrect: Transform misspelled artist names.
            username: The username whose playcount for this artist is queried.
            lang: ISO 639-1 language code for the biography.

        Returns:
            An `ArtistInfo` instance.
        """
        params = self._clean_params(
            {
                "artist": artist if not mbid else None,
                "mbid": mbid,
                "autocorrect": "1" if autocorrect else None,
                "username": username,
                "lang": lang,
            }
        )
        data = await self._get("artist.getInfo", params)
        return ArtistInfo.from_data(data.get("artist", {}))

    async def get_correction(self, artist: str) -> ArtistCorrection:
        """Use the Last.fm corrections database to find a valid artist name.

        Args:
            artist: The artist name to correct.

        Returns:
            An `ArtistCorrection` instance.
        """
        data = await self._get("artist.getCorrection", {"artist": artist})
        return ArtistCorrection.from_data(data)

    async def get_similar(
        self,
        artist: str,
        *,
        mbid: str | None = None,
        autocorrect: bool = False,
        limit: int | None = None,
    ) -> list[SimilarArtist]:
        """Get similar artists for this artist.

        Args:
            artist: The artist name to query.
            mbid: The MusicBrainz ID for the artist.
            autocorrect: Transform misspelled artist names.
            limit: Number of results to return.

        Returns:
            A list of `SimilarArtist` instances.
        """
        params = self._clean_params(
            {
                "artist": artist if not mbid else None,
                "mbid": mbid,
                "autocorrect": "1" if autocorrect else None,
                "limit": limit,
            }
        )
        data = await self._get("artist.getSimilar", params)
        container = data.get("similarartists", {})
        artists = self._ensure_list(container.get("artist"))
        return [SimilarArtist.from_data(a) for a in artists]

    async def get_tags(
        self,
        artist: str,
        user: str,
        *,
        mbid: str | None = None,
        autocorrect: bool = False,
    ) -> list[Tag]:
        """Get the tags applied by an individual user to an artist.

        Args:
            artist: The artist name.
            user: The username whose tags to fetch.
            mbid: The MusicBrainz ID for the artist.
            autocorrect: Transform misspelled artist names.

        Returns:
            A list of `Tag` instances.
        """
        params = self._clean_params(
            {
                "artist": artist if not mbid else None,
                "user": user,
                "mbid": mbid,
                "autocorrect": "1" if autocorrect else None,
            }
        )
        data = await self._get("artist.getTags", params)
        container = data.get("tags", {})
        tags = self._ensure_list(container.get("tag"))
        return [Tag.from_data(t) for t in tags]

    async def get_top_albums(
        self,
        artist: str,
        *,
        mbid: str | None = None,
        autocorrect: bool = False,
        limit: int | None = None,
        page: int | None = None,
    ) -> PaginatedResponse[TopAlbum]:
        """Get the top albums for an artist.

        Args:
            artist: The artist name.
            mbid: The MusicBrainz ID for the artist.
            autocorrect: Transform misspelled artist names.
            limit: Number of results per page.
            page: Page number to fetch.

        Returns:
            A paginated response containing `TopAlbum`.
        """
        params = self._clean_params(
            {
                "artist": artist if not mbid else None,
                "mbid": mbid,
                "autocorrect": "1" if autocorrect else None,
                "limit": limit,
                "page": page,
            }
        )
        data = await self._get("artist.getTopAlbums", params)
        container = data.get("topalbums", {})
        albums = self._ensure_list(container.get("album"))
        attr = container.get("@attr", {})
        return PaginatedResponse(
            items=[TopAlbum.from_data(a) for a in albums],
            attr=PaginationAttr.from_data(attr),
        )

    async def iter_top_albums(
        self,
        artist: str,
        *,
        mbid: str | None = None,
        autocorrect: bool = False,
        limit: int | None = None,
        max_pages: int | None = None,
        max_items: int | None = None,
    ) -> AsyncIterator[TopAlbum]:
        """Async iterator over top albums, auto-paginating."""
        page = 1
        items_yielded = 0
        while True:
            if max_pages is not None and page > max_pages:
                break
            result = await self.get_top_albums(
                artist, mbid=mbid, autocorrect=autocorrect, limit=limit, page=page
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
        artist: str,
        *,
        mbid: str | None = None,
        autocorrect: bool = False,
    ) -> list[TopTag]:
        """Get the top tags for an artist on Last.fm.

        Args:
            artist: The artist name.
            mbid: The MusicBrainz ID for the artist.
            autocorrect: Transform misspelled artist names.

        Returns:
            A list of `TopTag` instances.
        """
        params = self._clean_params(
            {
                "artist": artist if not mbid else None,
                "mbid": mbid,
                "autocorrect": "1" if autocorrect else None,
            }
        )
        data = await self._get("artist.getTopTags", params)
        container = data.get("toptags", {})
        tags = self._ensure_list(container.get("tag"))
        return [TopTag.from_data(t) for t in tags]

    async def get_top_tracks(
        self,
        artist: str,
        *,
        mbid: str | None = None,
        autocorrect: bool = False,
        limit: int | None = None,
        page: int | None = None,
    ) -> PaginatedResponse[TopTrack]:
        """Get the top tracks for an artist.

        Args:
            artist: The artist name.
            mbid: The MusicBrainz ID for the artist.
            autocorrect: Transform misspelled artist names.
            limit: Number of results per page.
            page: Page number to fetch.

        Returns:
            A paginated response containing `TopTrack`.
        """
        params = self._clean_params(
            {
                "artist": artist if not mbid else None,
                "mbid": mbid,
                "autocorrect": "1" if autocorrect else None,
                "limit": limit,
                "page": page,
            }
        )
        data = await self._get("artist.getTopTracks", params)
        container = data.get("toptracks", {})
        tracks = self._ensure_list(container.get("track"))
        attr = container.get("@attr", {})
        return PaginatedResponse(
            items=[TopTrack.from_data(t) for t in tracks],
            attr=PaginationAttr.from_data(attr),
        )

    async def iter_top_tracks(
        self,
        artist: str,
        *,
        mbid: str | None = None,
        autocorrect: bool = False,
        limit: int | None = None,
        max_pages: int | None = None,
        max_items: int | None = None,
    ) -> AsyncIterator[TopTrack]:
        """Async iterator over top tracks, auto-paginating."""
        page = 1
        items_yielded = 0
        while True:
            if max_pages is not None and page > max_pages:
                break
            result = await self.get_top_tracks(
                artist, mbid=mbid, autocorrect=autocorrect, limit=limit, page=page
            )
            for item in result.items:
                yield item
                items_yielded += 1
                if max_items is not None and items_yielded >= max_items:
                    return
            if page >= result.attr.total_pages or not result.items:
                break
            page += 1

    async def search(
        self,
        artist: str,
        *,
        limit: int | None = None,
        page: int | None = None,
    ) -> PaginatedResponse[TopArtist]:
        """Search for an artist by name.

        Args:
            artist: The artist name search query.
            limit: Number of results per page.
            page: Page number to fetch.

        Returns:
            A paginated response of matched artists.
        """
        params = self._clean_params(
            {
                "artist": artist,
                "limit": limit,
                "page": page,
            }
        )
        data = await self._get("artist.search", params)
        results = data.get("results", {})
        artists_container = results.get("artistmatches", {})
        artists = self._ensure_list(artists_container.get("artist"))

        # search attributes are shaped differently
        attr = {
            "page": results.get("opensearch:StartIndex", 1),
            "perPage": results.get("opensearch:itemsPerPage", 50),
            "total": results.get("opensearch:totalResults", 0),
            "totalPages": 0,  # search doesn't return totalPages directly
        }
        # compute totalPages
        try:
            total = int(attr["total"])
            per_page = int(attr["perPage"])
            attr["totalPages"] = (
                (total + per_page - 1) // per_page if per_page > 0 else 0
            )
        except (ValueError, TypeError):
            pass

        return PaginatedResponse(
            items=[TopArtist.from_data(a) for a in artists],
            attr=PaginationAttr.from_data(attr),
        )

    async def add_tags(
        self,
        artist: str,
        tags: list[str],
    ) -> None:
        """Tag an artist with one or more user tags.

        Requires user authentication (session key).

        Args:
            artist: The artist name.
            tags: A list of tags to apply. Maximum 10 tags.
        """
        params = {
            "artist": artist,
            "tags": ",".join(tags),
        }
        await self._post("artist.addTags", params)

    async def remove_tag(
        self,
        artist: str,
        tag: str,
    ) -> None:
        """Remove a user tag from an artist.

        Requires user authentication (session key).

        Args:
            artist: The artist name.
            tag: A single tag to remove.
        """
        params = {
            "artist": artist,
            "tag": tag,
        }
        await self._post("artist.removeTag", params)
