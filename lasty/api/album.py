"""Album API namespace — ``client.album.*`` methods."""

from __future__ import annotations


from .base import BaseAPI
from ..models.common import PaginatedResponse, PaginationAttr
from ..models.album import AlbumInfo, AlbumSearchResult
from ..models.tag import Tag, TopTag

__all__ = ["AlbumAPI"]


class AlbumAPI(BaseAPI):
    """Album-related API methods.

    Access via ``client.album``.
    """

    async def get_info(
        self,
        artist: str,
        album: str,
        *,
        mbid: str | None = None,
        autocorrect: bool = False,
        username: str | None = None,
        lang: str | None = None,
    ) -> AlbumInfo:
        """Get the metadata and tracklist for an album.

        Args:
            artist: The artist name.
            album: The album name.
            mbid: The MusicBrainz ID for the album.
            autocorrect: Transform misspelled artist names.
            username: The username whose playcount for this album is queried.
            lang: ISO 639-1 language code for the biography/wiki.

        Returns:
            An `AlbumInfo` instance.
        """
        params = self._clean_params(
            {
                "artist": artist if not mbid else None,
                "album": album if not mbid else None,
                "mbid": mbid,
                "autocorrect": "1" if autocorrect else None,
                "username": username,
                "lang": lang,
            }
        )
        data = await self._get("album.getInfo", params)
        return AlbumInfo.from_data(data.get("album", {}))

    async def get_tags(
        self,
        artist: str,
        album: str,
        user: str,
        *,
        mbid: str | None = None,
        autocorrect: bool = False,
    ) -> list[Tag]:
        """Get the tags applied by an individual user to an album.

        Args:
            artist: The artist name.
            album: The album name.
            user: The username whose tags to fetch.
            mbid: The MusicBrainz ID for the album.
            autocorrect: Transform misspelled artist names.

        Returns:
            A list of `Tag` instances.
        """
        params = self._clean_params(
            {
                "artist": artist if not mbid else None,
                "album": album if not mbid else None,
                "user": user,
                "mbid": mbid,
                "autocorrect": "1" if autocorrect else None,
            }
        )
        data = await self._get("album.getTags", params)
        container = data.get("tags", {})
        tags = self._ensure_list(container.get("tag"))
        return [Tag.from_data(t) for t in tags]

    async def get_top_tags(
        self,
        artist: str,
        album: str,
        *,
        mbid: str | None = None,
        autocorrect: bool = False,
    ) -> list[TopTag]:
        """Get the top tags for an album on Last.fm.

        Args:
            artist: The artist name.
            album: The album name.
            mbid: The MusicBrainz ID for the album.
            autocorrect: Transform misspelled artist names.

        Returns:
            A list of `TopTag` instances.
        """
        params = self._clean_params(
            {
                "artist": artist if not mbid else None,
                "album": album if not mbid else None,
                "mbid": mbid,
                "autocorrect": "1" if autocorrect else None,
            }
        )
        data = await self._get("album.getTopTags", params)
        container = data.get("toptags", {})
        tags = self._ensure_list(container.get("tag"))
        return [TopTag.from_data(t) for t in tags]

    async def search(
        self,
        album: str,
        *,
        limit: int | None = None,
        page: int | None = None,
    ) -> PaginatedResponse[AlbumSearchResult]:
        """Search for an album by name.

        Args:
            album: The album name search query.
            limit: Number of results per page.
            page: Page number to fetch.

        Returns:
            A paginated response of matched albums.
        """
        params = self._clean_params(
            {
                "album": album,
                "limit": limit,
                "page": page,
            }
        )
        data = await self._get("album.search", params)
        results = data.get("results", {})
        albums_container = results.get("albummatches", {})
        albums = self._ensure_list(albums_container.get("album"))

        # search attributes pagination details parsing
        attr = {
            "page": results.get("opensearch:StartIndex", 1),
            "perPage": results.get("opensearch:itemsPerPage", 50),
            "total": results.get("opensearch:totalResults", 0),
            "totalPages": 0,
        }
        try:
            total = int(attr["total"])
            per_page = int(attr["perPage"])
            attr["totalPages"] = (
                (total + per_page - 1) // per_page if per_page > 0 else 0
            )
        except (ValueError, TypeError):
            pass

        return PaginatedResponse(
            items=[AlbumSearchResult.from_data(a) for a in albums],
            attr=PaginationAttr.from_data(attr),
        )

    async def add_tags(
        self,
        artist: str,
        album: str,
        tags: list[str],
    ) -> None:
        """Tag an album with one or more user tags.

        Requires user authentication (session key).

        Args:
            artist: The artist name.
            album: The album name.
            tags: A list of tags to apply. Maximum 10 tags.
        """
        params = {
            "artist": artist,
            "album": album,
            "tags": ",".join(tags),
        }
        await self._post("album.addTags", params)

    async def remove_tag(
        self,
        artist: str,
        album: str,
        tag: str,
    ) -> None:
        """Remove a user tag from an album.

        Requires user authentication (session key).

        Args:
            artist: The artist name.
            album: The album name.
            tag: A single tag to remove.
        """
        params = {
            "artist": artist,
            "album": album,
            "tag": tag,
        }
        await self._post("album.removeTag", params)
