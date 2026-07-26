"""Artist models with inheritance hierarchy.

``BaseArtist`` provides the minimal fields shared across all artist
representations.  Richer variants inherit from it, adding fields specific
to their endpoint context.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from urllib.parse import quote_plus

from lasty._types import JSONDict
from lasty.models.common import Image
from lasty.models.tag import Tag

__all__ = [
    "BaseArtist",
    "ArtistSummary",
    "SimilarArtist",
    "TopArtist",
    "WeeklyChartArtist",
    "LibraryArtist",
    "ArtistStats",
    "ArtistBio",
    "ArtistInfo",
    "ArtistCorrection",
]


def _parse_artist_url(data: JSONDict, name: str) -> str:
    url = data.get("url")
    if url:
        return str(url)
    if name:
        return f"https://www.last.fm/music/{quote_plus(name)}"
    return ""


@dataclass(frozen=True, slots=True)
class BaseArtist:
    """Minimal artist representation shared across all endpoints.

    Attributes:
        name: The artist name.
        mbid: The MusicBrainz identifier (may be empty).
        url: The Last.fm URL for this artist.
    """

    name: str
    mbid: str
    url: str

    @classmethod
    def from_data(cls, data: JSONDict) -> BaseArtist:
        """Parse a minimal artist object.

        Args:
            data: A dict with ``name``, ``mbid``, and ``url`` keys.
        """
        name = data.get("name", "")
        return cls(
            name=name,
            mbid=data.get("mbid", ""),
            url=_parse_artist_url(data, name),
        )


@dataclass(frozen=True, slots=True)
class ArtistSummary(BaseArtist):
    """Artist with images, listeners, and playcount — used in chart/geo responses.

    Attributes:
        images: Available image variants.
        playcount: Total play count (may be ``0`` if not provided).
        listeners: Total listener count (may be ``0`` if not provided).
        streamable: Whether the artist is streamable.
    """

    images: list[Image] = field(default_factory=list)
    playcount: int = 0
    listeners: int = 0
    streamable: str = "0"

    @classmethod
    def from_data(cls, data: JSONDict) -> ArtistSummary:
        """Parse an artist summary from chart, geo, or tag top-artist responses.

        Args:
            data: The raw artist dict from the API.
        """
        name = data.get("name", "")
        return cls(
            name=name,
            mbid=data.get("mbid", ""),
            url=_parse_artist_url(data, name),
            images=Image.list_from_data(data.get("image")),
            playcount=int(data.get("playcount", 0)),
            listeners=int(data.get("listeners", 0)),
            streamable=data.get("streamable", "0"),
        )


@dataclass(frozen=True, slots=True)
class SimilarArtist(BaseArtist):
    """A similar artist returned by ``artist.getInfo`` or ``artist.getSimilar``.

    Attributes:
        images: Available image variants.
        match: Similarity score (0.0–1.0), present in ``getSimilar`` responses.
    """

    images: list[Image] = field(default_factory=list)
    match: float = 0.0

    @classmethod
    def from_data(cls, data: JSONDict) -> SimilarArtist:
        """Parse a similar artist object.

        Args:
            data: The raw similar artist dict from the API.
        """
        name = data.get("name", "")
        return cls(
            name=name,
            mbid=data.get("mbid", ""),
            url=_parse_artist_url(data, name),
            images=Image.list_from_data(data.get("image")),
            match=float(data.get("match", 0.0)),
        )


@dataclass(frozen=True, slots=True)
class TopArtist(BaseArtist):
    """An artist in a user's top artists list.

    Attributes:
        playcount: The user's play count for this artist.
        rank: The rank in the chart.
        images: Available image variants.
        streamable: Whether the artist is streamable.
    """

    playcount: int = 0
    rank: int = 0
    images: list[Image] = field(default_factory=list)
    streamable: str = "0"

    @classmethod
    def from_data(cls, data: JSONDict) -> TopArtist:
        """Parse a top artist from ``user.getTopArtists``.

        Args:
            data: The raw artist dict from the API.
        """
        attr = data.get("@attr", {})
        name = data.get("name", "")
        return cls(
            name=name,
            mbid=data.get("mbid", ""),
            url=_parse_artist_url(data, name),
            playcount=int(data.get("playcount", 0)),
            rank=int(attr.get("rank", 0)) if attr else 0,
            images=Image.list_from_data(data.get("image")),
            streamable=data.get("streamable", "0"),
        )


@dataclass(frozen=True, slots=True)
class WeeklyChartArtist(BaseArtist):
    """An artist in a user's weekly chart.

    Attributes:
        playcount: Play count during the chart period.
        rank: The rank in the weekly chart.
    """

    playcount: int = 0
    rank: int = 0

    @classmethod
    def from_data(cls, data: JSONDict) -> WeeklyChartArtist:
        """Parse an artist from ``user.getWeeklyArtistChart``.

        Args:
            data: The raw artist dict from the API.
        """
        attr = data.get("@attr", {})
        name = data.get("name", "")
        return cls(
            name=name,
            mbid=data.get("mbid", ""),
            url=_parse_artist_url(data, name),
            playcount=int(data.get("playcount", 0)),
            rank=int(attr.get("rank", 0)) if attr else 0,
        )


@dataclass(frozen=True, slots=True)
class LibraryArtist(BaseArtist):
    """An artist in a user's library, with play and tag counts.

    Attributes:
        playcount: The user's total play count for this artist.
        tagcount: The number of tags the user has applied.
        images: Available image variants.
        streamable: Whether the artist is streamable.
    """

    playcount: int = 0
    tagcount: int = 0
    images: list[Image] = field(default_factory=list)
    streamable: str = "0"

    @classmethod
    def from_data(cls, data: JSONDict) -> LibraryArtist:
        """Parse an artist from ``library.getArtists``.

        Args:
            data: The raw artist dict from the API.
        """
        name = data.get("name", "")
        return cls(
            name=name,
            mbid=data.get("mbid", ""),
            url=_parse_artist_url(data, name),
            playcount=int(data.get("playcount", 0)),
            tagcount=int(data.get("tagcount", 0)),
            images=Image.list_from_data(data.get("image")),
            streamable=data.get("streamable", "0"),
        )


@dataclass(frozen=True, slots=True)
class ArtistStats:
    """Global and per-user statistics for an artist.

    Attributes:
        listeners: Total unique listeners.
        playcount: Total play count.
        userplaycount: The authenticated user's play count (if ``username``
                       was provided in the request).
    """

    listeners: int
    playcount: int
    userplaycount: int | None = None

    @classmethod
    def from_data(cls, data: JSONDict | None) -> ArtistStats | None:
        """Parse artist stats.

        Args:
            data: A dict with ``listeners``, ``playcount``, and optionally
                  ``userplaycount`` keys, or ``None``.
        """
        if not data:
            return None
        upc = data.get("userplaycount")
        return cls(
            listeners=int(data.get("listeners", 0)),
            playcount=int(data.get("playcount", 0)),
            userplaycount=int(upc) if upc is not None else None,
        )


@dataclass(frozen=True, slots=True)
class ArtistBio:
    """Biography content for an artist.

    Attributes:
        published: The publication date string.
        summary: A short HTML summary.
        content: The full HTML biography.
        link_url: URL to the original wiki page.
    """

    published: str
    summary: str
    content: str
    link_url: str | None = None

    @classmethod
    def from_data(cls, data: JSONDict | None) -> ArtistBio | None:
        """Parse an artist biography.

        Args:
            data: A dict with ``published``, ``summary``, ``content``, and
                  ``links`` keys, or ``None``.
        """
        if not data:
            return None
        link_url: str | None = None
        links = data.get("links")
        if isinstance(links, dict):
            link = links.get("link", {})
            if isinstance(link, dict):
                link_url = link.get("href")
        return cls(
            published=data.get("published", ""),
            summary=data.get("summary", ""),
            content=data.get("content", ""),
            link_url=link_url,
        )


@dataclass(frozen=True, slots=True)
class ArtistInfo(BaseArtist):
    """Full artist information from ``artist.getInfo``.

    Attributes:
        images: Available image variants.
        streamable: Whether the artist is streamable.
        ontour: Whether the artist is currently on tour.
        stats: Global and per-user statistics.
        similar: List of similar artists.
        tags: List of top tags.
        bio: Artist biography/wiki content.
    """

    images: list[Image] = field(default_factory=list)
    streamable: str = "0"
    ontour: str = "0"
    stats: ArtistStats | None = None
    similar: list[SimilarArtist] = field(default_factory=list)
    tags: list[Tag] = field(default_factory=list)
    bio: ArtistBio | None = None

    @classmethod
    def from_data(cls, data: JSONDict) -> ArtistInfo:
        """Parse the full ``artist.getInfo`` response.

        Args:
            data: The ``artist`` object from the API response.
        """

        similar_data = data.get("similar", {})
        similar_list = (
            similar_data.get("artist", []) if isinstance(similar_data, dict) else []
        )

        tags_data = data.get("tags", {})
        tags_list = tags_data.get("tag", []) if isinstance(tags_data, dict) else []

        name = data.get("name", "")
        return cls(
            name=name,
            mbid=data.get("mbid", ""),
            url=_parse_artist_url(data, name),
            images=Image.list_from_data(data.get("image")),
            streamable=data.get("streamable", "0"),
            ontour=data.get("ontour", "0"),
            stats=ArtistStats.from_data(data.get("stats")),
            similar=[SimilarArtist.from_data(a) for a in similar_list],
            tags=[Tag.from_data(t) for t in tags_list],
            bio=ArtistBio.from_data(data.get("bio")),
        )


@dataclass(frozen=True, slots=True)
class ArtistCorrection:
    """A corrected artist name from ``artist.getCorrection``.

    Attributes:
        artist: The corrected artist.
    """

    artist: BaseArtist

    @classmethod
    def from_data(cls, data: JSONDict) -> ArtistCorrection:
        """Parse an artist correction response.

        Args:
            data: The correction object from the API.
        """
        corrections = data.get("corrections", {})
        correction = corrections.get("correction", {})
        artist_data = correction.get("artist", {})
        return cls(artist=BaseArtist.from_data(artist_data))

