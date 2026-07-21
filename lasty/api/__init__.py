"""API Namespace classes.

Exposes all namespace classes used by the client.
"""

from lasty.api.base import BaseAPI
from lasty.api.user import UserAPI
from lasty.api.artist import ArtistAPI
from lasty.api.album import AlbumAPI
from lasty.api.track import TrackAPI
from lasty.api.tag import TagAPI
from lasty.api.chart import ChartAPI
from lasty.api.geo import GeoAPI
from lasty.api.library import LibraryAPI
from lasty.api.auth import AuthAPI, Session

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
