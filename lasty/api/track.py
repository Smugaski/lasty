"""Track API namespace — ``client.track.*`` methods."""

from __future__ import annotations


from .base import BaseAPI
from ..models.common import PaginatedResponse, PaginationAttr
from ..models.track import (
    TrackInfo,
    TrackCorrection,
    SimilarTrack,
    BaseTrack,
    ScrobbleResult,
    NowPlayingResult,
)
from ..models.tag import Tag, TopTag

__all__ = ["TrackAPI"]


class TrackAPI(BaseAPI):
    """Track-related API methods.

    Access via ``client.track``.
    """

    async def get_info(
        self,
        artist: str,
        track: str,
        *,
        mbid: str | None = None,
        autocorrect: bool = False,
        username: str | None = None,
    ) -> TrackInfo:
        """Get the metadata for a track.

        Args:
            artist: The artist name.
            track: The track name.
            mbid: The MusicBrainz ID for the track.
            autocorrect: Transform misspelled artist/track names.
            username: The username whose playcount/loved status is queried.

        Returns:
            A `TrackInfo` instance.
        """
        params = self._clean_params(
            {
                "artist": artist if not mbid else None,
                "track": track if not mbid else None,
                "mbid": mbid,
                "autocorrect": "1" if autocorrect else None,
                "username": username,
            }
        )
        data = await self._get("track.getInfo", params)
        return TrackInfo.from_data(data.get("track", {}))

    async def get_correction(self, artist: str, track: str) -> TrackCorrection:
        """Use the Last.fm corrections database to find a valid track name.

        Args:
            artist: The artist name.
            track: The track name.

        Returns:
            A `TrackCorrection` instance.
        """
        data = await self._get(
            "track.getCorrection", {"artist": artist, "track": track}
        )
        return TrackCorrection.from_data(data)

    async def get_similar(
        self,
        artist: str,
        track: str,
        *,
        mbid: str | None = None,
        autocorrect: bool = False,
        limit: int | None = None,
    ) -> list[SimilarTrack]:
        """Get similar tracks for this track.

        Args:
            artist: The artist name.
            track: The track name.
            mbid: The MusicBrainz ID for the track.
            autocorrect: Transform misspelled artist/track names.
            limit: Number of results to return.

        Returns:
            A list of `SimilarTrack` instances.
        """
        params = self._clean_params(
            {
                "artist": artist if not mbid else None,
                "track": track if not mbid else None,
                "mbid": mbid,
                "autocorrect": "1" if autocorrect else None,
                "limit": limit,
            }
        )
        data = await self._get("track.getSimilar", params)
        container = data.get("similartracks", {})
        tracks = self._ensure_list(container.get("track"))
        return [SimilarTrack.from_data(t) for t in tracks]

    async def get_tags(
        self,
        artist: str,
        track: str,
        user: str,
        *,
        mbid: str | None = None,
        autocorrect: bool = False,
    ) -> list[Tag]:
        """Get the tags applied by an individual user to a track.

        Args:
            artist: The artist name.
            track: The track name.
            user: The username whose tags to fetch.
            mbid: The MusicBrainz ID for the track.
            autocorrect: Transform misspelled artist/track names.

        Returns:
            A list of `Tag` instances.
        """
        params = self._clean_params(
            {
                "artist": artist if not mbid else None,
                "track": track if not mbid else None,
                "user": user,
                "mbid": mbid,
                "autocorrect": "1" if autocorrect else None,
            }
        )
        data = await self._get("track.getTags", params)
        container = data.get("tags", {})
        tags = self._ensure_list(container.get("tag"))
        return [Tag.from_data(t) for t in tags]

    async def get_top_tags(
        self,
        artist: str,
        track: str,
        *,
        mbid: str | None = None,
        autocorrect: bool = False,
    ) -> list[TopTag]:
        """Get the top tags for a track on Last.fm.

        Args:
            artist: The artist name.
            track: The track name.
            mbid: The MusicBrainz ID for the track.
            autocorrect: Transform misspelled artist/track names.

        Returns:
            A list of `TopTag` instances.
        """
        params = self._clean_params(
            {
                "artist": artist if not mbid else None,
                "track": track if not mbid else None,
                "mbid": mbid,
                "autocorrect": "1" if autocorrect else None,
            }
        )
        data = await self._get("track.getTopTags", params)
        container = data.get("toptags", {})
        tags = self._ensure_list(container.get("tag"))
        return [TopTag.from_data(t) for t in tags]

    async def search(
        self,
        track: str,
        *,
        artist: str | None = None,
        limit: int | None = None,
        page: int | None = None,
    ) -> PaginatedResponse[BaseTrack]:
        """Search for a track by name.

        Args:
            track: The track name search query.
            artist: Filter by artist name (optional).
            limit: Number of results per page.
            page: Page number to fetch.

        Returns:
            A paginated response of matched tracks.
        """
        params = self._clean_params(
            {
                "track": track,
                "artist": artist,
                "limit": limit,
                "page": page,
            }
        )
        data = await self._get("track.search", params)
        results = data.get("results", {})
        tracks_container = results.get("trackmatches", {})
        tracks = self._ensure_list(tracks_container.get("track"))

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
            items=[BaseTrack.from_data(t) for t in tracks],
            attr=PaginationAttr.from_data(attr),
        )

    async def love(self, artist: str, track: str) -> None:
        """Love a track on a user's profile.

        Requires user authentication (session key).

        Args:
            artist: The artist name.
            track: The track name.
        """
        params = {
            "artist": artist,
            "track": track,
        }
        await self._post("track.love", params)

    async def unlove(self, artist: str, track: str) -> None:
        """Unlove a track on a user's profile.

        Requires user authentication (session key).

        Args:
            artist: The artist name.
            track: The track name.
        """
        params = {
            "artist": artist,
            "track": track,
        }
        await self._post("track.unlove", params)

    async def scrobble(
        self,
        artist: str,
        track: str,
        timestamp: int,
        *,
        album: str | None = None,
        album_artist: str | None = None,
        track_number: int | None = None,
        mbid: str | None = None,
        duration: int | None = None,
    ) -> ScrobbleResult:
        """Scrobble a single track play to Last.fm.

        Requires user authentication (session key).

        Args:
            artist: The artist name.
            track: The track name.
            timestamp: UNIX timestamp of when the track started playing.
            album: The album name (optional).
            album_artist: The album artist name (optional).
            track_number: The track number (optional).
            mbid: The track's MusicBrainz ID (optional).
            duration: The track duration in seconds (optional).

        Returns:
            A `ScrobbleResult` instance.
        """
        params = self._clean_params(
            {
                "artist": artist,
                "track": track,
                "timestamp": timestamp,
                "album": album,
                "albumArtist": album_artist,
                "trackNumber": track_number,
                "mbid": mbid,
                "duration": duration,
            }
        )
        data = await self._post("track.scrobble", params)
        return ScrobbleResult.from_data(data)

    async def update_now_playing(
        self,
        artist: str,
        track: str,
        *,
        album: str | None = None,
        album_artist: str | None = None,
        track_number: int | None = None,
        mbid: str | None = None,
        duration: int | None = None,
    ) -> NowPlayingResult:
        """Notify Last.fm that the user has started listening to a track.

        Requires user authentication (session key).

        Args:
            artist: The artist name.
            track: The track name.
            album: The album name (optional).
            album_artist: The album artist name (optional).
            track_number: The track number (optional).
            mbid: The track's MusicBrainz ID (optional).
            duration: The track duration in seconds (optional).

        Returns:
            A `NowPlayingResult` instance.
        """
        params = self._clean_params(
            {
                "artist": artist,
                "track": track,
                "album": album,
                "albumArtist": album_artist,
                "trackNumber": track_number,
                "mbid": mbid,
                "duration": duration,
            }
        )
        data = await self._post("track.updateNowPlaying", params)
        return NowPlayingResult.from_data(data)

    async def add_tags(
        self,
        artist: str,
        track: str,
        tags: list[str],
    ) -> None:
        """Tag a track with one or more user tags.

        Requires user authentication (session key).

        Args:
            artist: The artist name.
            track: The track name.
            tags: A list of tags to apply. Maximum 10 tags.
        """
        params = {
            "artist": artist,
            "track": track,
            "tags": ",".join(tags),
        }
        await self._post("track.addTags", params)

    async def remove_tag(
        self,
        artist: str,
        track: str,
        tag: str,
    ) -> None:
        """Remove a user tag from a track.

        Requires user authentication (session key).

        Args:
            artist: The artist name.
            track: The track name.
            tag: A single tag to remove.
        """
        params = {
            "artist": artist,
            "track": track,
            "tag": tag,
        }
        await self._post("track.removeTag", params)
