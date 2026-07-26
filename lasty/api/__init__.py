"""API Namespace classes.

Exposes all namespace classes used by the client.
"""

from .base import BaseAPI
from .user import UserAPI
from .artist import ArtistAPI
from .album import AlbumAPI
from .track import TrackAPI
from .tag import TagAPI
from .chart import ChartAPI
from .geo import GeoAPI
from .library import LibraryAPI
from .auth import AuthAPI, Session

__all__ = [
    "BaseAPI",
    "UserAPI",
    "ArtistAPI",
    "AlbumAPI",
    "TrackAPI",
    "TagAPI",
    "ChartAPI",
    "GeoAPI",
    "LibraryAPI",
    "AuthAPI",
    "Session",
]
