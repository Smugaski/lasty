"""Album models with inheritance hierarchy.

``BaseAlbum`` provides shared fields; richer variants add context-specific
data like tracks, tags, or playcount.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from urllib.parse import quote_plus

from .._types import JSONDict
from .common import Image, Wiki, Streamable
from .artist import BaseArtist
from .tag import Tag

__all__ = [
    "BaseAlbum",
    "AlbumSearchResult",
    "TopAlbum",
    "WeeklyChartAlbum",
    "AlbumTrack",
    "AlbumInfo",
    "TrackAlbum",
]


def _parse_album_url(data: JSONDict, artist: str, album_name: str) -> str:
    url = data.get("url")
    if url:
        return str(url)
    if artist and album_name:
        return (
            f"https://www.last.fm/music/{quote_plus(artist)}/{quote_plus(album_name)}"
        )
    return ""


@dataclass(frozen=True, slots=True)
class BaseAlbum:
    """Minimal album representation shared across endpoints.

    Attributes:
        name: The album name.
        mbid: The MusicBrainz identifier (may be empty).
        url: The Last.fm URL for this album.
        artist: The artist name or identifier.
    """

    name: str
    mbid: str
    url: str
    artist: str

    @classmethod
    def from_data(cls, data: JSONDict) -> BaseAlbum:
        """Parse a minimal album object.

        Args:
            data: A dict with ``name``, ``mbid``, ``url``, and ``artist`` keys.
                  The ``artist`` field may be a string or a dict with a ``name`` key.
        """
        name = data.get("name") or data.get("title", "")
        artist = data.get("artist", "")
        if isinstance(artist, dict):
            artist = artist.get("name", "")
        return cls(
            name=name,
            mbid=data.get("mbid", ""),
            url=_parse_album_url(data, artist, name),
            artist=artist,
        )


@dataclass(frozen=True, slots=True)
class TrackAlbum:
    """Album context embedded in a ``track.getInfo`` response.

    Attributes:
        artist: The album artist name.
        title: The album title.
        mbid: The MusicBrainz ID.
        url: The Last.fm URL.
        images: Available image variants.
        position: The track's position in the album.
    """

    artist: str
    title: str
    mbid: str
    url: str
    images: list[Image] = field(default_factory=list)
    position: int | None = None

    @classmethod
    def from_data(cls, data: JSONDict | None) -> TrackAlbum | None:
        """Parse an album context from a track info response.

        Args:
            data: The ``album`` object from a track response, or ``None``.
        """
        if not data:
            return None
        attr = data.get("@attr", {})
        pos = attr.get("position") if attr else None
        artist = data.get("artist", "")
        title = data.get("title", "") or data.get("name", "")
        return cls(
            artist=artist,
            title=title,
            mbid=data.get("mbid", ""),
            url=_parse_album_url(data, artist, title),
            images=Image.list_from_data(data.get("image")),
            position=int(pos) if pos is not None else None,
        )


@dataclass(frozen=True, slots=True)
class AlbumSearchResult(BaseAlbum):
    """An album from the ``album.search`` results.

    Attributes:
        images: Available image variants.
        streamable: Whether the album is streamable.
    """

    images: list[Image] = field(default_factory=list)
    streamable: str = "0"

    @classmethod
    def from_data(cls, data: JSONDict) -> AlbumSearchResult:
        """Parse an album search result.

        Args:
            data: The raw album dict from the search API.
        """
        name = data.get("name", "")
        artist = data.get("artist", "")
        if isinstance(artist, dict):
            artist = artist.get("name", "")
        return cls(
            name=name,
            mbid=data.get("mbid", ""),
            url=_parse_album_url(data, artist, name),
            artist=artist,
            images=Image.list_from_data(data.get("image")),
            streamable=data.get("streamable", "0"),
        )


@dataclass(frozen=True, slots=True)
class TopAlbum(BaseAlbum):
    """An album in a user's or artist's top albums list.

    Attributes:
        playcount: The play count for this album in the chart context.
        rank: The rank in the chart.
        images: Available image variants.
        artist_obj: The full artist object (when available).
    """

    playcount: int = 0
    rank: int = 0
    images: list[Image] = field(default_factory=list)
    artist_obj: BaseArtist | None = None

    @classmethod
    def from_data(cls, data: JSONDict) -> TopAlbum:
        """Parse a top album from ``user.getTopAlbums`` or ``artist.getTopAlbums``.

        Args:
            data: The raw album dict from the API.
        """
        name = data.get("name", "")
        attr = data.get("@attr", {})
        artist_raw = data.get("artist", "")
        artist_name: str
        artist_obj: BaseArtist | None = None
        if isinstance(artist_raw, dict):
            artist_name = artist_raw.get("name", "")
            artist_obj = BaseArtist.from_data(artist_raw)
        else:
            artist_name = str(artist_raw)

        return cls(
            name=name,
            mbid=data.get("mbid", ""),
            url=_parse_album_url(data, artist_name, name),
            artist=artist_name,
            playcount=int(data.get("playcount", 0)),
            rank=int(attr.get("rank", 0)) if attr else 0,
            images=Image.list_from_data(data.get("image")),
            artist_obj=artist_obj,
        )


@dataclass(frozen=True, slots=True)
class WeeklyChartAlbum(BaseAlbum):
    """An album in a user's weekly chart.

    Attributes:
        playcount: Play count during the chart period.
        rank: The rank in the weekly chart.
    """

    playcount: int = 0
    rank: int = 0

    @classmethod
    def from_data(cls, data: JSONDict) -> WeeklyChartAlbum:
        """Parse an album from ``user.getWeeklyAlbumChart``.

        Args:
            data: The raw album dict from the API.
        """
        name = data.get("name", "")
        attr = data.get("@attr", {})
        artist_raw = data.get("artist", "")
        if isinstance(artist_raw, dict):
            artist_name = str(
                artist_raw.get("#text") or artist_raw.get("name", "") or ""
            )
        else:
            artist_name = str(artist_raw)

        return cls(
            name=name,
            mbid=data.get("mbid", ""),
            url=_parse_album_url(data, artist_name, name),
            artist=artist_name,
            playcount=int(data.get("playcount", 0)),
            rank=int(attr.get("rank", 0)) if attr else 0,
        )


@dataclass(frozen=True, slots=True)
class AlbumTrack:
    """A track in an album's tracklist from ``album.getInfo``.

    Attributes:
        name: The track name.
        url: The Last.fm URL for this track.
        duration: The track duration in seconds.
        rank: The track's position in the album.
        artist: The track artist as a ``BaseArtist``.
        streamable: Streamability information.
    """

    name: str
    url: str
    duration: int
    rank: int
    artist: BaseArtist
    streamable: Streamable | None = None

    @classmethod
    def from_data(cls, data: JSONDict) -> AlbumTrack:
        """Parse a track from an album's tracklist.

        Args:
            data: The raw track dict from the API.
        """
        name = data.get("name", "")
        attr = data.get("@attr", {})
        artist_data = data.get("artist")
        artist_obj: BaseArtist
        if isinstance(artist_data, dict):
            artist_obj = BaseArtist.from_data(artist_data)
        elif isinstance(artist_data, str):
            artist_obj = BaseArtist.from_data({"name": artist_data})
        else:
            artist_obj = BaseArtist(name="", mbid="", url="")

        url = data.get("url")
        if not url and artist_obj.name and name:
            url = f"https://www.last.fm/music/{quote_plus(artist_obj.name)}/_/{quote_plus(name)}"

        return cls(
            name=name,
            url=str(url) if url else "",
            duration=int(data.get("duration", 0)),
            rank=int(attr.get("rank", 0)) if attr else 0,
            artist=artist_obj,
            streamable=Streamable.from_data(data.get("streamable")),
        )


@dataclass(frozen=True, slots=True)
class AlbumInfo(BaseAlbum):
    """Full album information from ``album.getInfo``.

    Attributes:
        images: Available image variants.
        listeners: Total unique listeners.
        playcount: Total play count.
        tracks: The album tracklist.
        tags: Top tags applied to the album.
        wiki: Wiki content for the album.
        userplaycount: The requesting user's play count (if ``username`` was provided).
    """

    images: list[Image] = field(default_factory=list)
    listeners: int = 0
    playcount: int = 0
    tracks: list[AlbumTrack] = field(default_factory=list)
    tags: list[Tag] = field(default_factory=list)
    wiki: Wiki | None = None
    userplaycount: int | None = None

    @classmethod
    def from_data(cls, data: JSONDict) -> AlbumInfo:
        """Parse the full ``album.getInfo`` response.

        Args:
            data: The ``album`` object from the API response.
        """
        name = data.get("name", "")
        artist_raw = data.get("artist", "")
        if isinstance(artist_raw, dict):
            artist_name = artist_raw.get("name", "")
        else:
            artist_name = str(artist_raw)

        tracks_data = data.get("tracks", {})
        tracks_list = (
            tracks_data.get("track", []) if isinstance(tracks_data, dict) else []
        )

        tags_data = data.get("tags", {})
        tags_list = tags_data.get("tag", []) if isinstance(tags_data, dict) else []

        upc = data.get("userplaycount")

        return cls(
            name=name,
            mbid=data.get("mbid", ""),
            url=_parse_album_url(data, artist_name, name),
            artist=artist_name,
            images=Image.list_from_data(data.get("image")),
            listeners=int(data.get("listeners", 0)),
            playcount=int(data.get("playcount", 0)),
            tracks=[AlbumTrack.from_data(t) for t in tracks_list],
            tags=[Tag.from_data(t) for t in tags_list],
            wiki=Wiki.from_data(data.get("wiki")),
            userplaycount=int(upc) if upc is not None else None,
        )
