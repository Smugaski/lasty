"""Base class for all API namespace classes.

Provides shared helpers for making GET/POST requests and stripping
response wrappers.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from .._types import JSONDict

if TYPE_CHECKING:
    from ..http import HTTPClient

__all__ = ["BaseAPI"]


class BaseAPI:
    """Base class that all API namespaces inherit from.

    Holds a reference to the shared `HTTPClient` and
    provides convenience methods for common request patterns.
    """

    __slots__ = ("_http",)

    def __init__(self, http: HTTPClient) -> None:
        self._http = http

    async def _get(self, method: str, params: dict[str, str] | None = None) -> JSONDict:
        """Make an unauthenticated GET request.

        Args:
            method: The API method name (e.g. ``"user.getInfo"``).
            params: Additional query parameters.

        Returns:
            The parsed JSON response.
        """
        return await self._http.get(method, params)

    async def _post(
        self,
        method: str,
        params: dict[str, str] | None = None,
        *,
        signed: bool = True,
    ) -> JSONDict:
        """Make an authenticated POST request.

        Args:
            method: The API method name (e.g. ``"track.love"``).
            params: Additional form parameters.
            signed: Whether to sign the request.

        Returns:
            The parsed JSON response.
        """
        return await self._http.post(method, params, signed=signed)

    @staticmethod
    def _clean_params(params: dict[str, str | int | None]) -> dict[str, str]:
        """Remove ``None`` values and stringify all remaining values.

        Args:
            params: Raw parameter dict with possible ``None`` values.

        Returns:
            A cleaned dict with all values as strings.
        """
        return {k: str(v) for k, v in params.items() if v is not None}

    @staticmethod
    def _ensure_list(data: object) -> list[JSONDict]:
        """Ensure data is a list of dicts.

        The Last.fm API sometimes returns a single object instead of a
        one-element list. This normalises that behaviour.

        Args:
            data: The raw data, which may be a list, dict, or ``None``.

        Returns:
            A list of dicts.
        """
        if data is None:
            return []
        if isinstance(data, dict):
            return [data]
        if isinstance(data, list):
            return data
        return []
