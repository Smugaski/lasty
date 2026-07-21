"""Tests for ChartAPI — mocked HTTP responses."""

from __future__ import annotations

import pytest

from lasty.api.chart import ChartAPI
from lasty.models.artist import ArtistSummary
from lasty.models.tag import TopTag
from lasty.models.track import TopTrack

from tests.conftest import BASE_URL_REGEX


@pytest.fixture
def chart_api(http_client_no_secret):
    return ChartAPI(http_client_no_secret)


class TestChartGetTopArtists:
    @pytest.mark.asyncio
    async def test_get_top_artists(self, chart_api, mock_aiohttp):
        mock_aiohttp.get(
            BASE_URL_REGEX,
            payload={
                "artists": {
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
                    "@attr": {"page": "1", "perPage": "50", "total": "1", "totalPages": "1"},
                }
            },
        )
        result = await chart_api.get_top_artists()
        assert len(result.items) == 1
        assert isinstance(result.items[0], ArtistSummary)


class TestChartGetTopTags:
    @pytest.mark.asyncio
    async def test_get_top_tags(self, chart_api, mock_aiohttp):
        mock_aiohttp.get(
            BASE_URL_REGEX,
            payload={
                "tags": {
                    "tag": [{"name": "rock", "url": "url", "count": "100"}],
                    "@attr": {"page": "1", "perPage": "50", "total": "1", "totalPages": "1"},
                }
            },
        )
        result = await chart_api.get_top_tags()
        assert len(result.items) == 1
        assert isinstance(result.items[0], TopTag)


class TestChartGetTopTracks:
    @pytest.mark.asyncio
    async def test_get_top_tracks(self, chart_api, mock_aiohttp):
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
                    "@attr": {"page": "1", "perPage": "50", "total": "1", "totalPages": "1"},
                }
            },
        )
        result = await chart_api.get_top_tracks()
        assert len(result.items) == 1
        assert isinstance(result.items[0], TopTrack)
