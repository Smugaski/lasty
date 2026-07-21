"""Enumerations for the Last.fm API."""

from __future__ import annotations

from enum import Enum

__all__ = [
    "ImageSize",
    "Period",
    "TaggingType",
]


class Period(str, Enum):
    """Time period for top charts and statistics.

    Used by endpoints like ``user.getTopArtists``, ``user.getTopAlbums``, etc.
    """

    OVERALL = "overall"
    """All time."""

    SEVEN_DAY = "7day"
    """Last 7 days."""

    ONE_MONTH = "1month"
    """Last month."""

    THREE_MONTH = "3month"
    """Last 3 months."""

    SIX_MONTH = "6month"
    """Last 6 months."""

    TWELVE_MONTH = "12month"
    """Last 12 months."""


class TaggingType(str, Enum):
    """Type of item that has been tagged by a user.

    Used by ``user.getPersonalTags``.
    """

    ARTIST = "artist"
    ALBUM = "album"
    TRACK = "track"


class ImageSize(str, Enum):
    """Size variants for Last.fm images."""

    SMALL = "small"
    """34px."""

    MEDIUM = "medium"
    """64px."""

    LARGE = "large"
    """174px."""

    EXTRALARGE = "extralarge"
    """300x300px."""

    MEGA = "mega"
    """300x300px (same resolution as extralarge)."""

    UNKNOWN = ""
    """Empty string size returned by some endpoints."""
