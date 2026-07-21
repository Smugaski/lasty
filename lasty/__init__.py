"""lasty — A fully typed, async Python client library for the Last.fm API.

Built on top of aiohttp, lasty provides clean model structures using
frozen dataclasses, PEP 561 compliance, and full namespace support
mirroring the Last.fm API methods.
"""

from lasty.client import LastFM
from lasty.enums import ImageSize, Period, TaggingType
from lasty.errors import (
    AuthenticationFailedError,
    InvalidAPIKeyError,
    InvalidFormatError,
    InvalidMethodError,
    InvalidMethodSignatureError,
    InvalidParametersError,
    InvalidResourceError,
    LastFMError,
    LoginRequiredError,
    OperationFailedError,
    InvalidSessionError,
    RateLimitError,
    ServiceOfflineError,
    ServiceUnavailableError,
    SuspendedAPIKeyError,
    TemporaryError,
)

__all__ = [
    "LastFM",
    # Enums
    "Period",
    "TaggingType",
    "ImageSize",
    # Errors
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
