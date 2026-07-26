"""Auth API namespace — ``client.auth.*`` methods."""

from __future__ import annotations

from dataclasses import dataclass
from .._types import JSONDict
from .base import BaseAPI

__all__ = ["Session", "AuthAPI"]


@dataclass(frozen=True, slots=True)
class Session:
    """A Last.fm user session.

    Attributes:
        name: The username of the authenticated user.
        key: The user's session key (pass to `LastFM` as ``session_key``).
        subscriber: Subscriber status (``"0"`` or ``"1"``).
    """

    name: str
    key: str
    subscriber: str

    @classmethod
    def from_data(cls, data: JSONDict) -> Session:
        """Parse a session object from the API response.

        Args:
            data: The session dictionary from the API.
        """
        return cls(
            name=data.get("name", ""),
            key=data.get("key", ""),
            subscriber=data.get("subscriber", "0"),
        )


class AuthAPI(BaseAPI):
    """Authentication API methods.

    Access via ``client.auth``.
    """

    async def get_token(self) -> str:
        """Request a unique token to authenticate a user.

        Requires signed request.

        Returns:
            A string token. The consumer must send the user to
            ``https://www.last.fm/api/auth/?api_key=...&token=...``
            for authorization.
        """
        # getToken is a signed request that uses GET
        data = await self._post("auth.getToken", signed=True)
        return str(data.get("token", ""))

    async def get_session(self, token: str) -> Session:
        """Fetch a Web Service Session Key using an authorized token.

        Requires signed request.

        Args:
            token: An authorized user token.

        Returns:
            A `Session` object containing the ``key`` (sk).
        """
        # getSession is a signed request that uses GET/POST, typically GET but signed.
        # We can perform it using GET or POST depending on signature constraints.
        # Last.fm official docs state this method requires signing.
        data = await self._post("auth.getSession", {"token": token}, signed=True)
        return Session.from_data(data.get("session", {}))

    def get_auth_url(self, token: str) -> str:
        """Helper to generate the authentication URL for user authorization.

        Args:
            token: The token retrieved via :meth:`get_token`.

        Returns:
            A URL string to open in a web browser.
        """
        return (
            f"https://www.last.fm/api/auth/?api_key={self._http._api_key}&token={token}"
        )
