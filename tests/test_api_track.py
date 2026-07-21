"""Tests for TrackAPI — mocked HTTP responses."""

from __future__ import annotations

import pytest

from lasty.api.track import TrackAPI
from lasty.models.track import (
    TrackInfo,
    TrackCorrection,
    SimilarTrack,
    BaseTrack,
    ScrobbleResult,
    NowPlayingResult,
)
from lasty.models.tag import Tag, TopTag

from tests.conftest import BASE_URL_REGEX


@pytest.fixture
def track_api(http_client_no_secret):
    return TrackAPI(http_client_no_secret)


@pytest.fixture
def track_api_authed(http_client):
    return TrackAPI(http_client)


class TestTrackGetInfo:
    @pytest.mark.asyncio
    async def test_get_info(self, track_api, mock_aiohttp):
        mock_aiohttp.get(
            BASE_URL_REGEX,
            payload={
                "track": {
                    "name": "Du Hast",
                    "mbid": "",
                    "url": "url",
                    "artist": {"name": "Rammstein", "mbid": "", "url": "url"},
                    "duration": "240000",
                    "listeners": "5000",
                    "playcount": "20000",
                    "toptags": {"tag": []},
                    "image": [],
                }
            },
        )
        result = await track_api.get_info("Rammstein", "Du Hast")
        assert isinstance(result, TrackInfo)
        assert result.name == "Du Hast"
        assert result.listeners == 5000


class TestTrackGetCorrection:
    @pytest.mark.asyncio
    async def test_get_correction(self, track_api, mock_aiohttp):
        mock_aiohttp.get(
            BASE_URL_REGEX,
            payload={
                "corrections": {
                    "correction": {
                        "track": {
                            "name": "Du Hast",
                            "mbid": "",
                            "url": "url",
                            "artist": {"name": "Rammstein", "mbid": "", "url": "url"},
                        }
                    }
                }
            },
        )
        result = await track_api.get_correction("Rammstein", "du hast")
        assert isinstance(result, TrackCorrection)
        assert result.track.name == "Du Hast"


class TestTrackGetSimilar:
    @pytest.mark.asyncio
    async def test_get_similar(self, track_api, mock_aiohttp):
        mock_aiohttp.get(
            BASE_URL_REGEX,
            payload={
                "similartracks": {
                    "track": [
                        {
                            "name": "Sonne",
                            "mbid": "",
                            "url": "url",
                            "artist": {"name": "Rammstein", "mbid": "", "url": "url"},
                            "match": "0.9",
                            "duration": "380",
                            "playcount": "1000",
                            "image": [],
                        }
                    ]
                }
            },
        )
        result = await track_api.get_similar("Rammstein", "Du Hast")
        assert len(result) == 1
        assert isinstance(result[0], SimilarTrack)


class TestTrackGetTags:
    @pytest.mark.asyncio
    async def test_get_tags(self, track_api, mock_aiohttp):
        mock_aiohttp.get(
            BASE_URL_REGEX,
            payload={"tags": {"tag": [{"name": "industrial metal", "url": "url"}]}},
        )
        result = await track_api.get_tags("Rammstein", "Du Hast", "Smugaski")
        assert len(result) == 1
        assert isinstance(result[0], Tag)


class TestTrackGetTopTags:
    @pytest.mark.asyncio
    async def test_get_top_tags(self, track_api, mock_aiohttp):
        mock_aiohttp.get(
            BASE_URL_REGEX,
            payload={
                "toptags": {
                    "tag": [{"name": "industrial metal", "url": "url", "count": "100"}]
                }
            },
        )
        result = await track_api.get_top_tags("Rammstein", "Du Hast")
        assert len(result) == 1
        assert isinstance(result[0], TopTag)


class TestTrackSearch:
    @pytest.mark.asyncio
    async def test_search(self, track_api, mock_aiohttp):
        mock_aiohttp.get(
            BASE_URL_REGEX,
            payload={
                "results": {
                    "opensearch:totalResults": "100",
                    "opensearch:startIndex": "0",
                    "opensearch:itemsPerPage": "30",
                    "trackmatches": {
                        "track": [
                            {
                                "name": "Du Hast",
                                "mbid": "",
                                "url": "url",
                                "artist": "Rammstein",
                            }
                        ]
                    },
                }
            },
        )
        result = await track_api.search("Du Hast")
        assert len(result.items) == 1
        assert isinstance(result.items[0], BaseTrack)


class TestTrackScrobble:
    @pytest.mark.asyncio
    async def test_scrobble(self, track_api_authed, mock_aiohttp):
        mock_aiohttp.post(
            BASE_URL_REGEX,
            payload={
                "scrobbles": {
                    "@attr": {"accepted": "1", "ignored": "0"},
                    "scrobble": {
                        "artist": {"#text": "Rammstein", "corrected": "0"},
                        "track": {"#text": "Du Hast", "corrected": "0"},
                    },
                }
            },
        )
        result = await track_api_authed.scrobble("Rammstein", "Du Hast", 1700000000)
        assert isinstance(result, ScrobbleResult)
        assert result.accepted == 1
        assert result.ignored == 0


class TestTrackUpdateNowPlaying:
    @pytest.mark.asyncio
    async def test_update_now_playing(self, track_api_authed, mock_aiohttp):
        mock_aiohttp.post(
            BASE_URL_REGEX,
            payload={
                "nowplaying": {
                    "artist": {"#text": "Rammstein", "corrected": "0"},
                    "track": {"#text": "Du Hast", "corrected": "0"},
                    "album": {"#text": "Sehnsucht", "corrected": "0"},
                    "ignoredMessage": {"#text": "", "code": "0"},
                }
            },
        )
        result = await track_api_authed.update_now_playing("Rammstein", "Du Hast")
        assert isinstance(result, NowPlayingResult)
        assert result.artist == "Rammstein"
        assert result.track == "Du Hast"


class TestTrackLoveUnlove:
    @pytest.mark.asyncio
    async def test_love(self, track_api_authed, mock_aiohttp):
        mock_aiohttp.post(BASE_URL_REGEX, payload={"lfm": {"status": "ok"}})
        await track_api_authed.love("Rammstein", "Du Hast")

    @pytest.mark.asyncio
    async def test_unlove(self, track_api_authed, mock_aiohttp):
        mock_aiohttp.post(BASE_URL_REGEX, payload={"lfm": {"status": "ok"}})
        await track_api_authed.unlove("Rammstein", "Du Hast")
