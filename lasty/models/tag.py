"""Tag models.

``Tag`` is the base representation, extended by ``TopTag`` (with a weighted
count) and ``TagInfo`` (with reach and wiki content).
"""

from __future__ import annotations

from dataclasses import dataclass

from .._types import JSONDict
from ..models.common import Wiki

__all__ = [
    "Tag",
    "TopTag",
    "UserTag",
    "TagInfo",
]


@dataclass(frozen=True, slots=True)
class Tag:
    """A minimal tag with name and URL.

    Attributes:
        name: The tag name.
        url: The Last.fm URL for this tag.
    """

    name: str
    url: str

    @classmethod
    def from_data(cls, data: JSONDict) -> Tag:
        """Parse a tag object.

        Args:
            data: A dict with ``name`` and ``url`` keys.
        """
        return cls(
            name=data.get("name", ""),
            url=data.get("url", ""),
        )


@dataclass(frozen=True, slots=True)
class TopTag(Tag):
    """A tag with a weighted application count (0–100).

    Used in ``getTopTags`` responses for artists, albums, and tracks.

    Attributes:
        count: A weighted count of how often the tag was applied (max 100).
    """

    count: int = 0

    @classmethod
    def from_data(cls, data: JSONDict) -> TopTag:
        """Parse a top tag object.

        Args:
            data: A dict with ``name``, ``url``, and ``count`` keys.
        """
        return cls(
            name=data.get("name", ""),
            url=data.get("url", ""),
            count=int(data.get("count", 0)),
        )


@dataclass(frozen=True, slots=True)
class UserTag(Tag):
    """A tag from a user's top tags, with a usage count.

    Attributes:
        count: How many times the user has applied this tag.
    """

    count: int = 0

    @classmethod
    def from_data(cls, data: JSONDict) -> UserTag:
        """Parse a user tag.

        Args:
            data: A dict with ``name``, ``url``, and ``count`` keys.
        """
        return cls(
            name=data.get("name", ""),
            url=data.get("url", ""),
            count=int(data.get("count", 0)),
        )


@dataclass(frozen=True, slots=True)
class TagInfo(Tag):
    """Full tag information from ``tag.getInfo``.

    Attributes:
        total: Total number of items tagged.
        reach: Number of unique users who have applied this tag.
        wiki: Wiki content for the tag.
    """

    total: int = 0
    reach: int = 0
    wiki: Wiki | None = None

    @classmethod
    def from_data(cls, data: JSONDict) -> TagInfo:
        """Parse a ``tag.getInfo`` response.

        Args:
            data: The ``tag`` object from the API response.
        """
        return cls(
            name=data.get("name", ""),
            url=data.get("url", ""),
            total=int(data.get("total", 0)),
            reach=int(data.get("reach", 0)),
            wiki=Wiki.from_data(data.get("wiki")),
        )
