"""Shared test fixtures and helpers for the lasty test suite."""

from __future__ import annotations

import pytest
import pytest_asyncio
import re

from aioresponses import aioresponses

from lasty.http import HTTPClient


API_KEY = "test_api_key_12345"
API_SECRET = "test_api_secret_67890"
SESSION_KEY = "test_session_key_abcde"
BASE_URL = "https://ws.audioscrobbler.com/2.0/"
BASE_URL_REGEX = re.compile(r"^https://ws\.audioscrobbler\.com/2\.0/.*")


@pytest.fixture
def mock_aiohttp():
    """Provide an aioresponses mock for HTTP interception."""
    with aioresponses() as m:
        yield m


@pytest_asyncio.fixture
async def http_client():
    """Provide a started HTTPClient for testing."""
    client = HTTPClient(
        api_key=API_KEY,
        api_secret=API_SECRET,
        session_key=SESSION_KEY,
    )
    await client.start()
    yield client
    await client.close()


@pytest_asyncio.fixture
async def http_client_no_secret():
    """Provide an HTTPClient without secret/session for read-only tests."""
    client = HTTPClient(api_key=API_KEY)
    await client.start()
    yield client
    await client.close()
