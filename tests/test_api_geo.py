"""Tests for GeoAPI — mocked HTTP responses."""

from __future__ import annotations

import pytest

from lasty.api.geo import GeoAPI
from lasty.models.artist import ArtistSummary
from lasty.models.track import TopTrack

from tests.conftest import BASE_URL_REGEX


@pytest.fixture
def geo_api(http_client_no_secret):
    return GeoAPI(http_client_no_secret)


class TestGeoGetTopArtists:
    @pytest.mark.asyncio
    async def test_get_top_artists(self, geo_api, mock_aiohttp):
        mock_aiohttp.get(
            BASE_URL_REGEX,
            payload={
                "topartists": {
                    "artist": [
                        {
                            "name": "Artist",
                            "mbid": "",
                            "url": "url",
                            "playcount": "100",
                            "listeners": "50",
                            "streamable": "0",
                            "image": [],
                        }
                    ],
                    "@attr": {
                        "page": "1",
                        "perPage": "50",
                        "total": "1",
                        "totalPages": "1",
                        "country": "Poland",
                    },
                }
            },
        )
        result = await geo_api.get_top_artists("Poland")
        assert len(result.items) == 1
        assert isinstance(result.items[0], ArtistSummary)
        assert result.items[0].name == "Artist"


class TestGeoGetTopTracks:
    @pytest.mark.asyncio
    async def test_get_top_tracks(self, geo_api, mock_aiohttp):
        mock_aiohttp.get(
            BASE_URL_REGEX,
            payload={
                "tracks": {
                    "track": [
                        {
                            "name": "Track",
                            "mbid": "",
                            "url": "url",
                            "artist": {"name": "Artist", "mbid": "", "url": "url"},
                            "playcount": "100",
                            "@attr": {"rank": "1"},
                            "duration": "200",
                            "image": [],
                        }
                    ],
                    "@attr": {
                        "page": "1",
                        "perPage": "50",
                        "total": "1",
                        "totalPages": "1",
                        "country": "Germany",
                    },
                }
            },
        )
        result = await geo_api.get_top_tracks("Germany")
        assert len(result.items) == 1
        assert isinstance(result.items[0], TopTrack)
