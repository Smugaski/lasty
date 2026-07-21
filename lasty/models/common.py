"""Common model primitives shared across all API responses.

These classes handle the Last.fm API's quirky JSON conventions:
- ``#text`` keys for text content
- ``@attr`` keys for metadata attributes
- String-encoded integers for numeric fields
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Generic, TypeVar

from lasty.enums import ImageSize
from lasty._types import JSONDict

__all__ = [
    "Image",
    "Wiki",
    "DateInfo",
    "Streamable",
    "PaginationAttr",
    "PaginatedResponse",
]

T = TypeVar("T")


@dataclass(frozen=True, slots=True)
class Image:
    """A Last.fm image in a specific size variant.

    Attributes:
        url: The direct URL to the image file.
        size: The size category of the image.
    """

    url: str
    size: ImageSize

    @classmethod
    def from_data(cls, data: JSONDict) -> Image:
        """Parse an image object from the API response.

        Args:
            data: A dict with ``#text`` (URL) and ``size`` keys.
        """
        raw_size = data.get("size", "")
        try:
            size = ImageSize(raw_size)
        except ValueError:
            size = ImageSize.UNKNOWN
        return cls(
            url=data.get("#text", ""),
            size=size,
        )

    @classmethod
    def list_from_data(cls, data: list[JSONDict] | None) -> list[Image]:
        """Parse a list of image objects.

        Args:
            data: A list of image dicts, or ``None``.
        """
        if not data:
            return []
        return [cls.from_data(img) for img in data]


@dataclass(frozen=True, slots=True)
class Wiki:
    """Wiki / biography content attached to artists, albums, tracks, or tags.

    Attributes:
        published: The publication date string (e.g. ``"06 Oct 2008, 13:22"``).
        summary: A short HTML summary of the content.
        content: The full HTML content.
    """

    published: str | None
    summary: str
    content: str

    @classmethod
    def from_data(cls, data: JSONDict | None) -> Wiki | None:
        """Parse a wiki object, returning ``None`` if absent.

        Args:
            data: A dict with ``published``, ``summary``, and ``content`` keys,
                  or ``None``.
        """
        if not data:
            return None
        return cls(
            published=data.get("published"),
            summary=data.get("summary", ""),
            content=data.get("content", ""),
        )


@dataclass(frozen=True, slots=True)
class DateInfo:
    """A timestamp returned by the API, with both UNIX and human-readable forms.

    Attributes:
        uts: The UNIX timestamp (seconds since epoch).
        text: The human-readable date string (e.g. ``"20 Oct 2020, 10:03"``).
    """

    uts: int
    text: str

    @classmethod
    def from_data(cls, data: JSONDict | None) -> DateInfo | None:
        """Parse a date object, returning ``None`` if absent.

        Args:
            data: A dict with ``uts`` and ``#text`` keys, or ``None``.
        """
        if not data:
            return None
        return cls(
            uts=int(data.get("uts", 0)),
            text=str(data.get("#text", "")),
        )


@dataclass(frozen=True, slots=True)
class Streamable:
    """Streamability information for a track.

    Attributes:
        fulltrack: Whether the full track is streamable (``"0"`` or ``"1"``).
        text: The streamable flag text value.
    """

    fulltrack: str
    text: str

    @classmethod
    def from_data(cls, data: JSONDict | str | None) -> Streamable | None:
        """Parse a streamable object.

        Some endpoints return streamable as a plain string instead of an object.

        Args:
            data: A dict with ``fulltrack`` and ``#text`` keys, a plain string,
                  or ``None``.
        """
        if data is None:
            return None
        if isinstance(data, str):
            return cls(fulltrack=data, text=data)
        return cls(
            fulltrack=data.get("fulltrack", "0"),
            text=data.get("#text", "0"),
        )


@dataclass(frozen=True, slots=True)
class PaginationAttr:
    """Pagination metadata from the ``@attr`` block of paginated responses.

    Attributes:
        page: The current page number (1-indexed).
        per_page: The number of results per page.
        total: The total number of results across all pages.
        total_pages: The total number of pages.
        user: The username context, if applicable.
    """

    page: int
    per_page: int
    total: int
    total_pages: int
    user: str | None = None

    @classmethod
    def from_data(cls, data: JSONDict | None) -> PaginationAttr:
        """Parse pagination attributes from the ``@attr`` block.

        Args:
            data: A dict with ``page``, ``perPage``, ``total``, and
                  ``totalPages`` keys, or ``None``.
        """
        if not data:
            return cls(page=1, per_page=50, total=0, total_pages=0)
        return cls(
            page=int(data.get("page", 1)),
            per_page=int(data.get("perPage", 50)),
            total=int(data.get("total", 0)),
            total_pages=int(data.get("totalPages", 0)),
            user=data.get("user"),
        )


@dataclass(frozen=True, slots=True)
class PaginatedResponse(Generic[T]):
    """A generic paginated response containing a list of items and pagination metadata.

    Attributes:
        items: The list of results for the current page.
        attr: Pagination metadata (page number, totals, etc.).
    """

    items: list[T]
    attr: PaginationAttr
