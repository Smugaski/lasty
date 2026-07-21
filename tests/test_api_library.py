"""Tests for LibraryAPI — mocked HTTP responses."""

from __future__ import annotations

import pytest

from lasty.api.library import LibraryAPI
from lasty.models.artist import LibraryArtist

from tests.conftest import BASE_URL_REGEX


@pytest.fixture
def library_api(http_client_no_secret):
    return LibraryAPI(http_client_no_secret)


class TestLibraryGetArtists:
    @pytest.mark.asyncio
    async def test_get_artists(self, library_api, mock_aiohttp):
        mock_aiohttp.get(
            BASE_URL_REGEX,
            payload={
                "artists": {
                    "artist": [
                        {
                            "name": "Rammstein",
                            "mbid": "",
                            "url": "url",
                            "playcount": "500",
                            "tagcount": "3",
                            "streamable": "0",
                            "image": [],
                        }
                    ],
                    "@attr": {
                        "page": "1",
                        "perPage": "50",
                        "total": "1",
                        "totalPages": "1",
                        "user": "Smugaski",
                    },
                }
            },
        )
        result = await library_api.get_artists("Smugaski")
        assert len(result.items) == 1
        assert isinstance(result.items[0], LibraryArtist)
        assert result.items[0].playcount == 500
        assert result.items[0].tagcount == 3

    @pytest.mark.asyncio
    async def test_get_artists_empty(self, library_api, mock_aiohttp):
        mock_aiohttp.get(
            BASE_URL_REGEX,
            payload={
                "artists": {
                    "@attr": {
                        "page": "1",
                        "perPage": "50",
                        "total": "0",
                        "totalPages": "0",
                        "user": "Smugaski",
                    },
                }
            },
        )
        result = await library_api.get_artists("Smugaski")
        assert len(result.items) == 0
