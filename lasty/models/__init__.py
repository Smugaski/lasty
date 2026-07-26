"""Model classes for Last.fm API responses.

All models are frozen dataclasses with ``from_data`` class methods that
parse the API's JSON responses into typed Python objects.
"""

from .common import (
    DateInfo,
    Image,
    PaginatedResponse,
    PaginationAttr,
    Streamable,
    Wiki,
)
from .artist import (
    ArtistBio,
    ArtistCorrection,
    ArtistInfo,
    ArtistStats,
    ArtistSummary,
    BaseArtist,
    LibraryArtist,
    SimilarArtist,
    TopArtist,
    WeeklyChartArtist,
)
from .album import (
    AlbumInfo,
    AlbumSearchResult,
    AlbumTrack,
    BaseAlbum,
    TopAlbum,
    TrackAlbum,
    WeeklyChartAlbum,
)
from .track import (
    BaseTrack,
    LovedTrack,
    NowPlayingResult,
    RecentTrack,
    ScrobbleResult,
    SimilarTrack,
    TopTrack,
    TrackCorrection,
    TrackInfo,
    WeeklyChartTrack,
)
from .user import (
    BaseUser,
    Friend,
    UserInfo,
)
from .tag import (
    Tag,
    TagInfo,
    TopTag,
    UserTag,
)
from .chart import (
    ChartDateRange,
    WeeklyChart,
    WeeklyChartAttr,
)

__all__ = [
    # Common
    "DateInfo",
    "Image",
    "PaginatedResponse",
    "PaginationAttr",
    "Streamable",
    "Wiki",
    # Artist
    "ArtistBio",
    "ArtistCorrection",
    "ArtistInfo",
    "ArtistStats",
    "ArtistSummary",
    "BaseArtist",
    "LibraryArtist",
    "SimilarArtist",
    "TopArtist",
    "WeeklyChartArtist",
    # Album
    "AlbumInfo",
    "AlbumSearchResult",
    "AlbumTrack",
    "BaseAlbum",
    "TopAlbum",
    "TrackAlbum",
    "WeeklyChartAlbum",
    # Track
    "BaseTrack",
    "LovedTrack",
    "NowPlayingResult",
    "RecentTrack",
    "ScrobbleResult",
    "SimilarTrack",
    "TopTrack",
    "TrackCorrection",
    "TrackInfo",
    "WeeklyChartTrack",
    # User
    "BaseUser",
    "Friend",
    "UserInfo",
    # Tag
    "Tag",
    "TagInfo",
    "TopTag",
    "UserTag",
    # Chart
    "ChartDateRange",
    "WeeklyChart",
    "WeeklyChartAttr",
]
