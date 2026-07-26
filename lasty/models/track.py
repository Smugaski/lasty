from __future__ import annotations

from dataclasses import dataclass, field
from urllib.parse import quote_plus

from lasty._types import JSONDict
from lasty.models.common import Image, Wiki, Streamable, DateInfo
from lasty.models.artist import BaseArtist
from lasty.models.album import TrackAlbum
from lasty.models.tag import Tag

__all__ = [
    "BaseTrack",
    "TopTrack",
    "LovedTrack",
    "RecentTrack",
    "WeeklyChartTrack",
    "SimilarTrack",
    "TrackInfo",
    "TrackCorrection",
    "ScrobbleResult",
    "NowPlayingResult",
]


def _parse_track_url(
    data: JSONDict, artist_name: str, track_name: str, album_name: str = ""
) -> str:
    url = data.get("url")
    if url:
        return str(url)
    if artist_name and track_name:
        artist_quoted = quote_plus(artist_name)
        track_quoted = quote_plus(track_name)
        if album_name:
            album_quoted = quote_plus(album_name)
            return f"https://www.last.fm/music/{artist_quoted}/{album_quoted}/_/{track_quoted}"
        return f"https://www.last.fm/music/{artist_quoted}/_/{track_quoted}"
    return ""


@dataclass(frozen=True, slots=True)
class BaseTrack:
    """Minimal track representation shared across endpoints.

    Attributes:
        name: The track name.
        mbid: The MusicBrainz identifier (may be empty).
        url: The Last.fm URL for this track.
        artist: The artist as a ``BaseArtist`` or ``None``.
        artist_name: The artist name as a plain string.
    """

    name: str
    mbid: str
    url: str
    artist: BaseArtist | None = None
    artist_name: str = ""

    @classmethod
    def from_data(cls, data: JSONDict) -> BaseTrack:
        """Parse a minimal track object.

        Args:
            data: A dict with ``name``, ``mbid``, ``url``, and ``artist`` keys.
                  The ``artist`` field may be a string or a dict.
        """
        name = data.get("name", "")
        artist_raw = data.get("artist")
        artist_obj: BaseArtist | None = None
        artist_name: str = ""
        if isinstance(artist_raw, dict):
            if "name" in artist_raw:
                artist_obj = BaseArtist.from_data(artist_raw)
                artist_name = artist_raw.get("name", "")
            else:
                artist_name = artist_raw.get("#text", "")
        elif isinstance(artist_raw, str):
            artist_name = artist_raw

        return cls(
            name=name,
            mbid=data.get("mbid", ""),
            url=_parse_track_url(data, artist_name, name),
            artist=artist_obj,
            artist_name=artist_name,
        )


@dataclass(frozen=True, slots=True)
class TopTrack(BaseTrack):
    """A track in a user's or artist's top tracks list.

    Attributes:
        artist: The artist as a ``BaseArtist``.
        playcount: The play count in the chart context.
        rank: The rank in the chart.
        duration: Track duration in seconds.
        images: Available image variants.
        streamable: Streamability information.
    """

    artist: BaseArtist
    playcount: int = 0
    rank: int = 0
    duration: int = 0
    images: list[Image] = field(default_factory=list)
    streamable: Streamable | None = None

    @classmethod
    def from_data(cls, data: JSONDict) -> TopTrack:
        """Parse a top track from ``user.getTopTracks`` or ``artist.getTopTracks``.

        Args:
            data: The raw track dict from the API.
        """
        attr = data.get("@attr", {})
        name = data.get("name", "")
        artist_raw = data.get("artist")
        artist_obj: BaseArtist
        if isinstance(artist_raw, dict):
            artist_obj = BaseArtist.from_data(artist_raw)
            artist_name = artist_raw.get("name", "")
        elif isinstance(artist_raw, str):
            artist_name = artist_raw
            artist_obj = BaseArtist.from_data({"name": artist_name})
        else:
            artist_name = ""
            artist_obj = BaseArtist(name="", mbid="", url="")

        return cls(
            name=name,
            mbid=data.get("mbid", ""),
            url=_parse_track_url(data, artist_name, name),
            artist=artist_obj,
            artist_name=artist_name,
            playcount=int(data.get("playcount", 0)),
            rank=int(attr.get("rank", 0)) if attr else 0,
            duration=int(data.get("duration", 0)),
            images=Image.list_from_data(data.get("image")),
            streamable=Streamable.from_data(data.get("streamable")),
        )


@dataclass(frozen=True, slots=True)
class LovedTrack(BaseTrack):
    """A track from a user's loved tracks list.

    Attributes:
        artist: The artist as a ``BaseArtist``.
        date: When the track was loved.
        images: Available image variants.
        streamable: Streamability information.
    """

    artist: BaseArtist
    date: DateInfo | None = None
    images: list[Image] = field(default_factory=list)
    streamable: Streamable | None = None

    @classmethod
    def from_data(cls, data: JSONDict) -> LovedTrack:
        """Parse a loved track from ``user.getLovedTracks``.

        Args:
            data: The raw track dict from the API.
        """
        name = data.get("name", "")
        artist_raw = data.get("artist")
        artist_obj: BaseArtist
        if isinstance(artist_raw, dict):
            artist_obj = BaseArtist.from_data(artist_raw)
            artist_name = artist_raw.get("name", "")
        elif isinstance(artist_raw, str):
            artist_name = artist_raw
            artist_obj = BaseArtist.from_data({"name": artist_name})
        else:
            artist_name = ""
            artist_obj = BaseArtist(name="", mbid="", url="")

        return cls(
            name=name,
            mbid=data.get("mbid", ""),
            url=_parse_track_url(data, artist_name, name),
            artist=artist_obj,
            artist_name=artist_name,
            date=DateInfo.from_data(data.get("date")),
            images=Image.list_from_data(data.get("image")),
            streamable=Streamable.from_data(data.get("streamable")),
        )


@dataclass(frozen=True, slots=True)
class RecentTrack(BaseTrack):
    """A recently scrobbled track from ``user.getRecentTracks``.

    Attributes:
        album_name: The album name (from the ``album`` dict's ``#text`` key).
        album_mbid: The album's MusicBrainz ID.
        images: Available image variants.
        date: When the track was scrobbled (``None`` if currently playing).
        now_playing: ``True`` if the track is currently being played.
        loved: Whether the user has loved this track (only in extended mode).
        streamable: Streamability flag.
    """

    album_name: str = ""
    album_mbid: str = ""
    images: list[Image] = field(default_factory=list)
    date: DateInfo | None = None
    now_playing: bool = False
    loved: str | None = None
    streamable: str = "0"

    @classmethod
    def from_data(cls, data: JSONDict) -> RecentTrack:
        """Parse a recent track from ``user.getRecentTracks``.

        Handles both standard and extended response formats.

        Args:
            data: The raw track dict from the API.
        """
        name = data.get("name", "")
        attr = data.get("@attr", {})
        now_playing = attr.get("nowplaying", "false") == "true" if attr else False

        artist_raw = data.get("artist")
        artist_obj: BaseArtist | None = None
        artist_name: str = ""
        if isinstance(artist_raw, dict):
            if "name" in artist_raw:
                # Extended format
                artist_obj = BaseArtist.from_data(artist_raw)
                artist_name = artist_raw.get("name", "")
            else:
                # Standard format: {"mbid": "...", "#text": "..."}
                artist_name = artist_raw.get("#text", "")
        elif isinstance(artist_raw, str):
            artist_name = artist_raw

        album_raw = data.get("album", {})
        album_name = ""
        album_mbid = ""
        if isinstance(album_raw, dict):
            album_name = album_raw.get("#text") or album_raw.get("name", "")
            album_mbid = album_raw.get("mbid", "")
        elif isinstance(album_raw, str):
            album_name = album_raw

        return cls(
            name=name,
            mbid=data.get("mbid", ""),
            url=_parse_track_url(data, artist_name, name, album_name),
            artist=artist_obj,
            artist_name=artist_name,
            album_name=album_name,
            album_mbid=album_mbid,
            images=Image.list_from_data(data.get("image")),
            date=DateInfo.from_data(data.get("date")),
            now_playing=now_playing,
            loved=data.get("loved"),
            streamable=data.get("streamable", "0"),
        )


@dataclass(frozen=True, slots=True)
class WeeklyChartTrack(BaseTrack):
    """A track in a user's weekly chart.

    Attributes:
        playcount: Play count during the chart period.
        rank: The rank in the weekly chart.
        images: Available image variants.
    """

    playcount: int = 0
    rank: int = 0
    images: list[Image] = field(default_factory=list)

    @classmethod
    def from_data(cls, data: JSONDict) -> WeeklyChartTrack:
        """Parse a track from ``user.getWeeklyTrackChart``.

        Args:
            data: The raw track dict from the API.
        """
        attr = data.get("@attr", {})
        name = data.get("name", "")
        artist_raw = data.get("artist")
        artist_name: str = ""
        if isinstance(artist_raw, dict):
            artist_name = artist_raw.get("#text") or artist_raw.get("name", "")
        elif isinstance(artist_raw, str):
            artist_name = artist_raw

        return cls(
            name=name,
            mbid=data.get("mbid", ""),
            url=_parse_track_url(data, artist_name, name),
            artist_name=artist_name,
            playcount=int(data.get("playcount", 0)),
            rank=int(attr.get("rank", 0)) if attr else 0,
            images=Image.list_from_data(data.get("image")),
        )


@dataclass(frozen=True, slots=True)
class SimilarTrack(BaseTrack):
    """A similar track from ``track.getSimilar``.

    Attributes:
        artist: The artist as a ``BaseArtist``.
        match: Similarity score (0.0–1.0).
        duration: Track duration in seconds.
        playcount: Total play count.
        images: Available image variants.
    """

    artist: BaseArtist
    match: float = 0.0
    duration: int = 0
    playcount: int = 0
    images: list[Image] = field(default_factory=list)

    @classmethod
    def from_data(cls, data: JSONDict) -> SimilarTrack:
        """Parse a similar track.

        Args:
            data: The raw track dict from the API.
        """
        name = data.get("name", "")
        artist_raw = data.get("artist")
        artist_obj: BaseArtist
        if isinstance(artist_raw, dict):
            artist_obj = BaseArtist.from_data(artist_raw)
            artist_name = artist_raw.get("name", "")
        elif isinstance(artist_raw, str):
            artist_name = artist_raw
            artist_obj = BaseArtist.from_data({"name": artist_name})
        else:
            artist_name = ""
            artist_obj = BaseArtist(name="", mbid="", url="")

        return cls(
            name=name,
            mbid=data.get("mbid", ""),
            url=_parse_track_url(data, artist_name, name),
            artist=artist_obj,
            artist_name=artist_name,
            match=float(data.get("match", 0.0)),
            duration=int(data.get("duration", 0)),
            playcount=int(data.get("playcount", 0)),
            images=Image.list_from_data(data.get("image")),
        )


@dataclass(frozen=True, slots=True)
class TrackInfo(BaseTrack):
    """Full track information from ``track.getInfo``.

    Attributes:
        artist: The artist as a ``BaseArtist``.
        duration: Track duration in milliseconds.
        listeners: Total unique listeners.
        playcount: Total play count.
        streamable: Streamability information.
        album: The album this track belongs to (if any).
        toptags: Top tags applied to this track.
        wiki: Wiki content for this track.
        userplaycount: The requesting user's play count (if ``username`` was provided).
        userloved: Whether the requesting user has loved this track.
    """

    artist: BaseArtist
    duration: int = 0
    listeners: int = 0
    playcount: int = 0
    streamable: Streamable | None = None
    album: TrackAlbum | None = None
    toptags: list[Tag] = field(default_factory=list)
    wiki: Wiki | None = None
    userplaycount: int | None = None
    userloved: str | None = None

    @classmethod
    def from_data(cls, data: JSONDict) -> TrackInfo:
        """Parse the full ``track.getInfo`` response.

        Args:
            data: The ``track`` object from the API response.
        """
        name = data.get("name", "")
        artist_raw = data.get("artist")
        artist_obj: BaseArtist
        if isinstance(artist_raw, dict):
            artist_obj = BaseArtist.from_data(artist_raw)
            artist_name = artist_raw.get("name", "")
        elif isinstance(artist_raw, str):
            artist_name = artist_raw
            artist_obj = BaseArtist.from_data({"name": artist_name})
        else:
            artist_name = ""
            artist_obj = BaseArtist(name="", mbid="", url="")

        album_data = data.get("album")
        album_name = ""
        if isinstance(album_data, dict):
            album_name = album_data.get("title", "") or album_data.get("name", "")

        toptags_data = data.get("toptags", {})
        toptags_list = (
            toptags_data.get("tag", []) if isinstance(toptags_data, dict) else []
        )

        upc = data.get("userplaycount")

        return cls(
            name=name,
            mbid=data.get("mbid", ""),
            url=_parse_track_url(data, artist_name, name, album_name),
            artist=artist_obj,
            artist_name=artist_name,
            duration=int(data.get("duration", 0)),
            listeners=int(data.get("listeners", 0)),
            playcount=int(data.get("playcount", 0)),
            streamable=Streamable.from_data(data.get("streamable")),
            album=TrackAlbum.from_data(album_data if isinstance(album_data, dict) else None),
            toptags=[Tag.from_data(t) for t in toptags_list],
            wiki=Wiki.from_data(data.get("wiki")),
            userplaycount=int(upc) if upc is not None else None,
            userloved=data.get("userloved"),
        )


@dataclass(frozen=True, slots=True)
class TrackCorrection:
    """A corrected track name from ``track.getCorrection``.

    Attributes:
        track: The corrected track.
    """

    track: BaseTrack

    @classmethod
    def from_data(cls, data: JSONDict) -> TrackCorrection:
        """Parse a track correction response.

        Args:
            data: The correction response from the API.
        """
        corrections = data.get("corrections", {})
        correction = corrections.get("correction", {})
        track_data = correction.get("track", {})
        return cls(track=BaseTrack.from_data(track_data))


@dataclass(frozen=True, slots=True)
class ScrobbleResult:
    """Result from a ``track.scrobble`` request.

    Attributes:
        accepted: Number of scrobbles accepted.
        ignored: Number of scrobbles ignored.
    """

    accepted: int
    ignored: int

    @classmethod
    def from_data(cls, data: JSONDict) -> ScrobbleResult:
        """Parse a scrobble response.

        Args:
            data: The ``scrobbles`` object from the API response.
        """
        attr = data.get("scrobbles", {}).get("@attr", {})
        return cls(
            accepted=int(attr.get("accepted", 0)),
            ignored=int(attr.get("ignored", 0)),
        )


@dataclass(frozen=True, slots=True)
class NowPlayingResult:
    """Result from a ``track.updateNowPlaying`` request.

    Attributes:
        artist: The corrected artist name.
        track: The corrected track name.
        album: The corrected album name (if provided).
        ignoredmessage: Reason the request was ignored (if applicable).
    """

    artist: str
    track: str
    album: str
    ignoredmessage: str

    @classmethod
    def from_data(cls, data: JSONDict) -> NowPlayingResult:
        """Parse a now-playing response.

        Args:
            data: The ``nowplaying`` object from the API response.
        """
        np = data.get("nowplaying", {})
        return cls(
            artist=(
                np.get("artist", {}).get("#text", "")
                if isinstance(np.get("artist"), dict)
                else ""
            ),
            track=(
                np.get("track", {}).get("#text", "")
                if isinstance(np.get("track"), dict)
                else ""
            ),
            album=(
                np.get("album", {}).get("#text", "")
                if isinstance(np.get("album"), dict)
                else ""
            ),
            ignoredmessage=(
                np.get("ignoredMessage", {}).get("#text", "")
                if isinstance(np.get("ignoredMessage"), dict)
                else ""
            ),
        )
