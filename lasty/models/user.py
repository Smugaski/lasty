"""User models.

``BaseUser`` provides shared fields; ``UserInfo`` and ``Friend`` extend it
with profile-specific data.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from lasty._types import JSONDict
from lasty.models.common import Image, DateInfo

__all__ = [
    "BaseUser",
    "UserInfo",
    "Friend",
]


@dataclass(frozen=True, slots=True)
class BaseUser:
    """Minimal user representation.

    Attributes:
        name: The Last.fm username.
        url: The Last.fm profile URL.
    """

    name: str
    url: str

    @classmethod
    def from_data(cls, data: JSONDict) -> BaseUser:
        """Parse a minimal user object.

        Args:
            data: A dict with ``name`` and ``url`` keys.
        """
        return cls(
            name=data.get("name", ""),
            url=data.get("url", ""),
        )


@dataclass(frozen=True, slots=True)
class UserInfo(BaseUser):
    """Full user profile from ``user.getInfo``.

    Attributes:
        playcount: Total scrobble count.
        playlists: Number of playlists.
        images: Profile image variants.
        registered: Account registration timestamp.
        country: The user's country.
        age: The user's age (``0`` if not set).
        gender: The user's gender (``"n"`` if not set).
        subscriber: Whether the user is a subscriber (``"0"`` or ``"1"``).
        realname: The user's real name.
        type: The account type (e.g. ``"user"``).
        bootstrap: Bootstrap flag (``"0"`` or ``"1"``).
    """

    playcount: int = 0
    playlists: int = 0
    images: list[Image] = field(default_factory=list)
    registered: DateInfo | None = None
    country: str = ""
    age: int = 0
    gender: str = "n"
    subscriber: str = "0"
    realname: str = ""
    type: str = "user"
    bootstrap: str = "0"

    @classmethod
    def from_data(cls, data: JSONDict) -> UserInfo:
        """Parse a ``user.getInfo`` response.

        Args:
            data: The ``user`` object from the API response.
        """
        return cls(
            name=data.get("name", ""),
            url=data.get("url", ""),
            playcount=int(data.get("playcount", 0)),
            playlists=int(data.get("playlists", 0)),
            images=Image.list_from_data(data.get("image")),
            registered=DateInfo.from_data(data.get("registered")),
            country=data.get("country", ""),
            age=int(data.get("age", 0)),
            gender=data.get("gender", "n"),
            subscriber=data.get("subscriber", "0"),
            realname=data.get("realname", ""),
            type=data.get("type", "user"),
            bootstrap=data.get("bootstrap", "0"),
        )


@dataclass(frozen=True, slots=True)
class Friend(BaseUser):
    """A user's friend from ``user.getFriends``.

    Shares the same structure as ``UserInfo`` but without all profile fields.

    Attributes:
        playcount: Total scrobble count.
        images: Profile image variants.
        registered: Account registration timestamp.
        country: The friend's country.
        realname: The friend's real name.
        subscriber: Whether the friend is a subscriber.
        type: The account type.
        bootstrap: Bootstrap flag.
    """

    playcount: int = 0
    images: list[Image] = field(default_factory=list)
    registered: DateInfo | None = None
    country: str = ""
    realname: str = ""
    subscriber: str = "0"
    type: str = "user"
    bootstrap: str = "0"

    @classmethod
    def from_data(cls, data: JSONDict) -> Friend:
        """Parse a friend from ``user.getFriends``.

        Args:
            data: The raw user dict from the API.
        """
        return cls(
            name=data.get("name", ""),
            url=data.get("url", ""),
            playcount=int(data.get("playcount", 0)),
            images=Image.list_from_data(data.get("image")),
            registered=DateInfo.from_data(data.get("registered")),
            country=data.get("country", ""),
            realname=data.get("realname", ""),
            subscriber=data.get("subscriber", "0"),
            type=data.get("type", "user"),
            bootstrap=data.get("bootstrap", "0"),
        )
