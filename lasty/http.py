"""Low-level HTTP client wrapping ``aiohttp`` for Last.fm API requests.

Handles session lifecycle, request signing, error detection, and
automatic retry with exponential backoff on rate-limit (429) and
temporary errors.
"""

from __future__ import annotations

import asyncio
import logging

import aiohttp

from ._types import JSONDict
from .auth import generate_signature
from .errors import LastFMError, RateLimitError, TemporaryError

__all__ = ["HTTPClient"]

logger = logging.getLogger("lasty.http")

_BASE_URL = "https://ws.audioscrobbler.com/2.0/"
_DEFAULT_USER_AGENT = "lasty/0.1.0 (Python/aiohttp)"

# Retry configuration
_MAX_RETRIES = 3
_BASE_BACKOFF = 1.0  # seconds


class HTTPClient:
    """Async HTTP client for the Last.fm API.

    Manages the ``aiohttp.ClientSession`` lifecycle and provides ``get``
    and ``post`` methods that handle parameter injection, signing, and
    error parsing.

    This class is not intended to be used directly; use `LastFM`
    instead.

    Args:
        api_key: Your Last.fm API key.
        api_secret: Your Last.fm API secret (required for authenticated calls).
        session_key: A user session key (required for authenticated calls).
        user_agent: Custom User-Agent header string.
    """

    def __init__(
        self,
        api_key: str,
        api_secret: str | None = None,
        session_key: str | None = None,
        *,
        user_agent: str | None = None,
    ) -> None:
        self._api_key = api_key
        self._api_secret = api_secret
        self._session_key = session_key
        self._user_agent = user_agent or _DEFAULT_USER_AGENT
        self._session: aiohttp.ClientSession | None = None

    async def start(self) -> None:
        """Create the underlying ``aiohttp.ClientSession``.

        Called automatically by :meth:`lasty.LastFM.__aenter__`.
        """
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession(
                headers={"User-Agent": self._user_agent},
            )

    async def close(self) -> None:
        """Close the underlying ``aiohttp.ClientSession``.

        Called automatically by :meth:`lasty.LastFM.__aexit__`.
        """
        if self._session and not self._session.closed:
            await self._session.close()
            self._session = None

    def _ensure_session(self) -> aiohttp.ClientSession:
        """Return the active session or raise if not started."""
        if self._session is None or self._session.closed:
            raise RuntimeError(
                "HTTPClient is not started. Use 'async with LastFM(...) as client:' "
                "to ensure the session is properly managed."
            )
        return self._session

    async def get(self, method: str, params: dict[str, str] | None = None) -> JSONDict:
        """Make an unauthenticated GET request to the Last.fm API.

        Args:
            method: The API method name (e.g. ``"user.getInfo"``).
            params: Additional query parameters.

        Returns:
            The parsed JSON response as a dict.

        Raises:
            LastFMError: If the API returns an error response.
        """
        request_params: dict[str, str] = {
            "method": method,
            "api_key": self._api_key,
            "format": "json",
        }
        if params:
            request_params.update(params)

        return await self._request("GET", request_params)

    async def post(
        self,
        method: str,
        params: dict[str, str] | None = None,
        *,
        signed: bool = True,
    ) -> JSONDict:
        """Make an authenticated POST request to the Last.fm API.

        The request is automatically signed with the API secret and
        session key.

        Args:
            method: The API method name (e.g. ``"track.love"``).
            params: Additional form parameters.
            signed: Whether to sign the request (default ``True``).

        Returns:
            The parsed JSON response as a dict.

        Raises:
            LastFMError: If the API returns an error response.
            RuntimeError: If ``api_secret`` or ``session_key`` is not set
                          when signing is required.
        """
        request_params: dict[str, str] = {
            "method": method,
            "api_key": self._api_key,
            "format": "json",
        }
        if params:
            request_params.update(params)

        if signed:
            if not self._api_secret:
                raise RuntimeError(
                    "api_secret is required for authenticated API calls. "
                    "Pass it when creating the LastFM client."
                )
            if self._session_key:
                request_params["sk"] = self._session_key

            request_params["api_sig"] = generate_signature(
                request_params, self._api_secret
            )

        return await self._request("POST", request_params)

    async def _request(
        self,
        http_method: str,
        params: dict[str, str],
    ) -> JSONDict:
        """Execute an HTTP request with retry logic.

        Retries automatically on:
        - Rate limit errors (HTTP 429 / Last.fm error code 29)
        - Temporary errors (Last.fm error code 16)
        - Server errors (HTTP 5xx)

        Uses exponential backoff: 1s, 2s, 4s.

        Args:
            http_method: ``"GET"`` or ``"POST"``.
            params: The request parameters.

        Returns:
            The parsed JSON response.

        Raises:
            LastFMError: If the API returns a non-retryable error, or
                         all retries are exhausted.
        """
        session = self._ensure_session()
        last_error: Exception | None = None

        for attempt in range(_MAX_RETRIES + 1):
            if attempt > 0:
                backoff = _BASE_BACKOFF * (2 ** (attempt - 1))
                logger.warning(
                    "Retry %d/%d after %.1fs backoff for %s",
                    attempt,
                    _MAX_RETRIES,
                    backoff,
                    params.get("method", "unknown"),
                )
                await asyncio.sleep(backoff)

            try:
                if http_method == "GET":
                    resp = await session.get(_BASE_URL, params=params)
                else:
                    resp = await session.post(_BASE_URL, data=params)

                # Handle HTTP-level rate limiting
                if resp.status == 429:
                    retry_after = resp.headers.get("Retry-After")
                    if retry_after and attempt < _MAX_RETRIES:
                        await asyncio.sleep(float(retry_after))
                        continue
                    text = await resp.text()
                    raise RateLimitError(f"Rate limit exceeded (HTTP 429): {text}", 29)

                # Handle server errors with retry
                if resp.status >= 500 and attempt < _MAX_RETRIES:
                    last_error = LastFMError(f"Server error (HTTP {resp.status})", 0)
                    continue

                data: JSONDict = await resp.json(content_type=None)

            except aiohttp.ClientError as exc:
                if attempt < _MAX_RETRIES:
                    last_error = exc
                    continue
                raise LastFMError(f"HTTP request failed: {exc}") from exc

            # Check for API-level errors
            if "error" in data:
                error = LastFMError.from_response(data)

                # Retry on temporary errors and rate limits
                if isinstance(error, (TemporaryError, RateLimitError)):
                    if attempt < _MAX_RETRIES:
                        last_error = error
                        continue

                raise error

            return data

        # Should not reach here, but just in case:
        if last_error:
            if isinstance(last_error, LastFMError):
                raise last_error
            raise LastFMError(
                f"Request failed after {_MAX_RETRIES} retries: {last_error}"
            )
        raise LastFMError("Request failed for unknown reasons")
