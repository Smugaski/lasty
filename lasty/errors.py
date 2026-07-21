"""Exception hierarchy for Last.fm API errors.

Each exception maps to a specific Last.fm error code. The API often returns
HTTP 200 even on errors, so response payloads must always be checked.
"""

from __future__ import annotations

__all__ = [
    "LastFMError",
    "ServiceUnavailableError",
    "InvalidMethodError",
    "AuthenticationFailedError",
    "InvalidFormatError",
    "InvalidParametersError",
    "InvalidResourceError",
    "OperationFailedError",
    "InvalidSessionError",
    "InvalidAPIKeyError",
    "ServiceOfflineError",
    "InvalidMethodSignatureError",
    "TemporaryError",
    "LoginRequiredError",
    "SuspendedAPIKeyError",
    "RateLimitError",
]

# Mapping of Last.fm error codes to exception classes, populated at module level.
_ERROR_CODE_MAP: dict[int, type[LastFMError]] = {}


class LastFMError(Exception):
    """Base exception for all Last.fm API errors.

    Attributes:
        code: The Last.fm error code.
        message: The error message returned by the API.
    """

    code: int = 0

    def __init__(self, message: str, code: int = 0) -> None:
        self.code = code
        self.message = message
        super().__init__(f"[Error {code}] {message}")

    def __init_subclass__(cls, *, code: int = 0, **kwargs: object) -> None:
        super().__init_subclass__(**kwargs)
        if code:
            cls.code = code
            _ERROR_CODE_MAP[code] = cls

    @classmethod
    def from_response(cls, data: dict[str, object]) -> LastFMError:
        """Create the appropriate exception from an API error response.

        Args:
            data: The parsed JSON response containing ``error`` and ``message`` keys.

        Returns:
            A specific ``LastFMError`` subclass matching the error code, or the
            base ``LastFMError`` if the code is unrecognised.
        """
        raw_error = data.get("error", 0)
        error_code = int(raw_error) if isinstance(raw_error, (int, str)) else 0
        message = str(data.get("message", "Unknown error"))
        exc_cls = _ERROR_CODE_MAP.get(error_code, cls)
        return exc_cls(message, error_code)


class ServiceUnavailableError(LastFMError, code=2):
    """Error code 2: Service offline / unavailable.

    Usually emitted when Last.fm is having server issues or the endpoint
    is malformed.
    """


class InvalidMethodError(LastFMError, code=3):
    """Error code 3: Invalid method.

    The requested API method does not exist.
    """


class AuthenticationFailedError(LastFMError, code=4):
    """Error code 4: Authentication failed.

    The session token has been revoked or is invalid.
    """


class InvalidFormatError(LastFMError, code=5):
    """Error code 5: Invalid response format.

    The ``format`` parameter must be ``json`` or ``xml``.
    """


class InvalidParametersError(LastFMError, code=6):
    """Error code 6: Invalid parameters.

    A required parameter is missing, invalid, or the resource was not found.
    """


class InvalidResourceError(LastFMError, code=7):
    """Error code 7: Invalid resource specified.

    The requested resource does not exist or cannot provide the requested data.
    """


class OperationFailedError(LastFMError, code=8):
    """Error code 8: Operation failed.

    A generic server-side error occurred.
    """


class InvalidSessionError(LastFMError, code=9):
    """Error code 9: Invalid session key.

    The session key is invalid or expired. Re-authenticate the user.
    """


class InvalidAPIKeyError(LastFMError, code=10):
    """Error code 10: Invalid API key.

    The API key provided is not valid.
    """


class ServiceOfflineError(LastFMError, code=11):
    """Error code 11: Service offline.

    A specific part of the Last.fm backend is temporarily offline.
    """


class InvalidMethodSignatureError(LastFMError, code=13):
    """Error code 13: Invalid method signature.

    The ``api_sig`` parameter is incorrect or malformed.
    """


class TemporaryError(LastFMError, code=16):
    """Error code 16: Temporary error.

    A transient server error; the request can be retried.
    """


class LoginRequiredError(LastFMError, code=17):
    """Error code 17: Login required.

    The requested user profile has privacy set to non-public.
    """


class SuspendedAPIKeyError(LastFMError, code=26):
    """Error code 26: Suspended API key.

    The API key has been banned due to terms of service violations.
    """


class RateLimitError(LastFMError, code=29):
    """Error code 29: Rate limit exceeded.

    Too many requests have been made in a short period.
    """
