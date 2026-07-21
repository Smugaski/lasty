"""Tests for TagAPI — mocked HTTP responses."""

from __future__ import annotations

import pytest

from lasty.api.tag import TagAPI
from lasty.models.tag import TagInfo, Tag, TopTag
from lasty.models.album import TopAlbum
from lasty.models.artist import ArtistSummary
from lasty.models.track import TopTrack
from lasty.models.chart import ChartDateRange

from tests.conftest import BASE_URL_REGEX


@pytest.fixture
def tag_api(http_client_no_secret):
    return TagAPI(http_client_no_secret)


class TestTagGetInfo:
    @pytest.mark.asyncio
    async def test_get_info(self, tag_api, mock_aiohttp):
        mock_aiohttp.get(
            BASE_URL_REGEX,
            payload={
                "tag": {
                    "name": "rock",
                    "url": "url",
                    "total": "1000",
                    "reach": "500",
                    "wiki": {"published": "date", "summary": "s", "content": "c"},
                }
            },
        )
        result = await tag_api.get_info("rock")
        assert isinstance(result, TagInfo)
        assert result.name == "rock"
        assert result.total == 1000


class TestTagGetSimilar:
    @pytest.mark.asyncio
    async def test_get_similar(self, tag_api, mock_aiohttp):
        mock_aiohttp.get(
            BASE_URL_REGEX,
            payload={
                "similartags": {
                    "tag": [{"name": "alternative", "url": "url"}],
                }
            },
        )
        result = await tag_api.get_similar("rock")
        assert len(result) == 1
        assert isinstance(result[0], Tag)


class TestTagGetTopAlbums:
    @pytest.mark.asyncio
    async def test_get_top_albums(self, tag_api, mock_aiohttp):
        mock_aiohttp.get(
            BASE_URL_REGEX,
            payload={
                "albums": {
                    "album": [
                        {
                            "name": "Album",
                            "mbid": "",
                            "url": "url",
                            "artist": {"name": "Artist", "mbid": "", "url": "url"},
                            "playcount": "100",
                            "@attr": {"rank": "1"},
                            "image": [],
                        }
                    ],
                    "@attr": {"page": "1", "perPage": "50", "total": "1", "totalPages": "1"},
                }
            },
        )
        result = await tag_api.get_top_albums("rock")
        assert len(result.items) == 1
        assert isinstance(result.items[0], TopAlbum)


class TestTagGetTopArtists:
    @pytest.mark.asyncio
    async def test_get_top_artists(self, tag_api, mock_aiohttp):
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
                    "@attr": {"page": "1", "perPage": "50", "total": "1", "totalPages": "1"},
                }
            },
        )
        result = await tag_api.get_top_artists("rock")
        assert len(result.items) == 1
        assert isinstance(result.items[0], ArtistSummary)


class TestTagGetTopTags:
    @pytest.mark.asyncio
    async def test_get_top_tags(self, tag_api, mock_aiohttp):
        mock_aiohttp.get(
            BASE_URL_REGEX,
            payload={
                "toptags": {
                    "tag": [{"name": "rock", "url": "url", "count": "100"}],
                }
            },
        )
        result = await tag_api.get_top_tags()
        assert len(result) == 1
        assert isinstance(result[0], TopTag)


class TestTagGetTopTracks:
    @pytest.mark.asyncio
    async def test_get_top_tracks(self, tag_api, mock_aiohttp):
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
        result = await tag_api.get_top_tracks("rock")
        assert len(result.items) == 1
        assert isinstance(result.items[0], TopTrack)


class TestTagGetWeeklyChartList:
    @pytest.mark.asyncio
    async def test_get_weekly_chart_list(self, tag_api, mock_aiohttp):
        mock_aiohttp.get(
            BASE_URL_REGEX,
            payload={
                "weeklychartlist": {
                    "chart": [
                        {"from": "1000", "to": "2000"},
                        {"from": "2000", "to": "3000"},
                    ],
                }
            },
        )
        result = await tag_api.get_weekly_chart_list("rock")
        assert len(result) == 2
        assert isinstance(result[0], ChartDateRange)
