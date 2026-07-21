"""Authentication utilities for the Last.fm API.

Implements the MD5 signature generation algorithm required for all
authenticated (write) API calls.
"""

from __future__ import annotations

import hashlib

__all__ = ["generate_signature"]


def generate_signature(params: dict[str, str], secret: str) -> str:
    """Generate an API method signature for authenticated requests.

    The signature is computed by:
    1. Sorting all parameters alphabetically by key (excluding ``format``).
    2. Concatenating key-value pairs into a single string.
    3. Appending the API secret.
    4. Computing the MD5 hash (UTF-8 encoded).

    Args:
        params: The request parameters (excluding ``api_sig`` itself).
                The ``format`` parameter is automatically excluded.
        secret: The Last.fm API secret.

    Returns:
        The uppercase hexadecimal MD5 hash to use as the ``api_sig`` parameter.

    Example:
        >>> generate_signature(
        ...     {"api_key": "KEY", "method": "auth.getSession", "token": "TOKEN"},
        ...     "SECRET",
        ... )
        '...'  # 32-character hex string
    """
    # Sort alphabetically and exclude 'format' as per Last.fm spec.
    sorted_params = sorted((k, v) for k, v in params.items() if k != "format")

    # Build the signature string: key1value1key2value2...secret
    sig_string = "".join(f"{k}{v}" for k, v in sorted_params) + secret

    # MD5 hash with UTF-8 encoding
    return hashlib.md5(sig_string.encode("utf-8")).hexdigest().upper()
