"""Tests for UserAPI — mocked HTTP responses."""

from __future__ import annotations

import pytest

from lasty.api.user import UserAPI
from lasty.models.user import UserInfo, Friend
from lasty.models.track import LovedTrack, RecentTrack, TopTrack, WeeklyChartTrack
from lasty.models.artist import TopArtist, WeeklyChartArtist
from lasty.models.album import TopAlbum, WeeklyChartAlbum
from lasty.models.tag import UserTag
from lasty.models.chart import ChartDateRange
from lasty.enums import Period, TaggingType

from tests.conftest import BASE_URL_REGEX


@pytest.fixture
def user_api(http_client_no_secret):
    return UserAPI(http_client_no_secret)


class TestUserGetInfo:
    @pytest.mark.asyncio
    async def test_get_info(self, user_api, mock_aiohttp):
        mock_aiohttp.get(
            BASE_URL_REGEX,
            payload={
                "user": {
                    "name": "Smugaski",
                    "url": "https://www.last.fm/user/Smugaski",
                    "playcount": "100000",
                    "playlists": "3",
                    "image": [],
                    "country": "PL",
                    "age": "0",
                    "gender": "n",
                    "subscriber": "0",
                    "realname": "Smugaski",
                    "type": "user",
                    "bootstrap": "0",
                }
            },
        )
        result = await user_api.get_info("Smugaski")
        assert isinstance(result, UserInfo)
        assert result.name == "Smugaski"
        assert result.playcount == 100000


class TestUserGetFriends:
    @pytest.mark.asyncio
    async def test_get_friends(self, user_api, mock_aiohttp):
        mock_aiohttp.get(
            BASE_URL_REGEX,
            payload={
                "friends": {
                    "user": [
                        {
                            "name": "friend1",
                            "url": "url",
                            "playcount": "5000",
                            "image": [],
                            "country": "US",
                            "realname": "A Friend",
                            "subscriber": "0",
                            "type": "user",
                            "bootstrap": "0",
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
        result = await user_api.get_friends("Smugaski")
        assert len(result.items) == 1
        assert isinstance(result.items[0], Friend)
        assert result.items[0].name == "friend1"


class TestUserGetLovedTracks:
    @pytest.mark.asyncio
    async def test_get_loved_tracks(self, user_api, mock_aiohttp):
        mock_aiohttp.get(
            BASE_URL_REGEX,
            payload={
                "lovedtracks": {
                    "track": [
                        {
                            "name": "Du Hast",
                            "mbid": "",
                            "url": "url",
                            "artist": {"name": "Rammstein", "mbid": "", "url": "url"},
                            "date": {"uts": "1603187000", "#text": "20 Oct 2020"},
                            "image": [],
                        }
                    ],
                    "@attr": {"page": "1", "perPage": "50", "total": "1", "totalPages": "1"},
                }
            },
        )
        result = await user_api.get_loved_tracks("Smugaski")
        assert len(result.items) == 1
        assert isinstance(result.items[0], LovedTrack)


class TestUserGetRecentTracks:
    @pytest.mark.asyncio
    async def test_get_recent_tracks(self, user_api, mock_aiohttp):
        mock_aiohttp.get(
            BASE_URL_REGEX,
            payload={
                "recenttracks": {
                    "track": [
                        {
                            "name": "Du Hast",
                            "mbid": "",
                            "url": "url",
                            "artist": {"#text": "Rammstein", "mbid": ""},
                            "album": {"#text": "Sehnsucht", "mbid": ""},
                            "image": [],
                            "date": {"uts": "1603187000", "#text": "20 Oct 2020"},
                            "streamable": "0",
                        }
                    ],
                    "@attr": {"page": "1", "perPage": "50", "total": "1", "totalPages": "1"},
                }
            },
        )
        result = await user_api.get_recent_tracks("Smugaski")
        assert len(result.items) == 1
        assert isinstance(result.items[0], RecentTrack)
        assert result.items[0].artist_name == "Rammstein"


class TestUserGetTopAlbums:
    @pytest.mark.asyncio
    async def test_get_top_albums(self, user_api, mock_aiohttp):
        mock_aiohttp.get(
            BASE_URL_REGEX,
            payload={
                "topalbums": {
                    "album": [
                        {
                            "name": "Mutter",
                            "mbid": "",
                            "url": "url",
                            "artist": {"name": "Rammstein", "mbid": "", "url": "url"},
                            "playcount": "999",
                            "@attr": {"rank": "1"},
                            "image": [],
                        }
                    ],
                    "@attr": {"page": "1", "perPage": "50", "total": "1", "totalPages": "1"},
                }
            },
        )
        result = await user_api.get_top_albums("Smugaski", period=Period.OVERALL)
        assert len(result.items) == 1
        assert isinstance(result.items[0], TopAlbum)


class TestUserGetTopArtists:
    @pytest.mark.asyncio
    async def test_get_top_artists(self, user_api, mock_aiohttp):
        mock_aiohttp.get(
            BASE_URL_REGEX,
            payload={
                "topartists": {
                    "artist": [
                        {
                            "name": "Rammstein",
                            "mbid": "",
                            "url": "url",
                            "playcount": "500",
                            "@attr": {"rank": "1"},
                            "streamable": "0",
                            "image": [],
                        }
                    ],
                    "@attr": {"page": "1", "perPage": "50", "total": "1", "totalPages": "1"},
                }
            },
        )
        result = await user_api.get_top_artists("Smugaski")
        assert len(result.items) == 1
        assert isinstance(result.items[0], TopArtist)


class TestUserGetTopTracks:
    @pytest.mark.asyncio
    async def test_get_top_tracks(self, user_api, mock_aiohttp):
        mock_aiohttp.get(
            BASE_URL_REGEX,
            payload={
                "toptracks": {
                    "track": [
                        {
                            "name": "Du Hast",
                            "mbid": "",
                            "url": "url",
                            "artist": {"name": "Rammstein", "mbid": "", "url": "url"},
                            "playcount": "777",
                            "@attr": {"rank": "1"},
                            "duration": "240",
                            "image": [],
                        }
                    ],
                    "@attr": {"page": "1", "perPage": "50", "total": "1", "totalPages": "1"},
                }
            },
        )
        result = await user_api.get_top_tracks("Smugaski", period=Period.SEVEN_DAY)
        assert len(result.items) == 1
        assert isinstance(result.items[0], TopTrack)


class TestUserGetTopTags:
    @pytest.mark.asyncio
    async def test_get_top_tags(self, user_api, mock_aiohttp):
        mock_aiohttp.get(
            BASE_URL_REGEX,
            payload={
                "toptags": {
                    "tag": [{"name": "industrial metal", "url": "url", "count": "50"}],
                }
            },
        )
        result = await user_api.get_top_tags("Smugaski")
        assert len(result) == 1
        assert isinstance(result[0], UserTag)
        assert result[0].count == 50


class TestUserGetPersonalTags:
    @pytest.mark.asyncio
    async def test_get_personal_tags_artist(self, user_api, mock_aiohttp):
        mock_aiohttp.get(
            BASE_URL_REGEX,
            payload={
                "taggings": {
                    "artists": {
                        "artist": [{"name": "Rammstein", "mbid": "", "url": "url"}]
                    },
                    "@attr": {"page": "1", "perPage": "50", "total": "1", "totalPages": "1"},
                }
            },
        )
        result = await user_api.get_personal_tags("Smugaski", "industrial metal", TaggingType.ARTIST)
        assert len(result.items) == 1


class TestUserWeeklyCharts:
    @pytest.mark.asyncio
    async def test_get_weekly_album_chart(self, user_api, mock_aiohttp):
        mock_aiohttp.get(
            BASE_URL_REGEX,
            payload={
                "weeklyalbumchart": {
                    "album": [
                        {
                            "name": "Mutter",
                            "mbid": "",
                            "url": "url",
                            "artist": {"#text": "Rammstein"},
                            "playcount": "10",
                            "@attr": {"rank": "1"},
                        }
                    ],
                    "@attr": {"user": "Smugaski", "from": "1000", "to": "2000"},
                }
            },
        )
        result = await user_api.get_weekly_album_chart("Smugaski")
        assert len(result.items) == 1
        assert isinstance(result.items[0], WeeklyChartAlbum)

    @pytest.mark.asyncio
    async def test_get_weekly_artist_chart(self, user_api, mock_aiohttp):
        mock_aiohttp.get(
            BASE_URL_REGEX,
            payload={
                "weeklyartistchart": {
                    "artist": [
                        {
                            "name": "Rammstein",
                            "mbid": "",
                            "url": "url",
                            "playcount": "10",
                            "@attr": {"rank": "1"},
                        }
                    ],
                    "@attr": {"user": "Smugaski", "from": "1000", "to": "2000"},
                }
            },
        )
        result = await user_api.get_weekly_artist_chart("Smugaski")
        assert len(result.items) == 1
        assert isinstance(result.items[0], WeeklyChartArtist)

    @pytest.mark.asyncio
    async def test_get_weekly_track_chart(self, user_api, mock_aiohttp):
        mock_aiohttp.get(
            BASE_URL_REGEX,
            payload={
                "weeklytrackchart": {
                    "track": [
                        {
                            "name": "Du Hast",
                            "mbid": "",
                            "url": "url",
                            "artist": {"#text": "Rammstein"},
                            "playcount": "10",
                            "@attr": {"rank": "1"},
                            "image": [],
                        }
                    ],
                    "@attr": {"user": "Smugaski", "from": "1000", "to": "2000"},
                }
            },
        )
        result = await user_api.get_weekly_track_chart("Smugaski")
        assert len(result.items) == 1
        assert isinstance(result.items[0], WeeklyChartTrack)

    @pytest.mark.asyncio
    async def test_get_weekly_chart_list(self, user_api, mock_aiohttp):
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
        result = await user_api.get_weekly_chart_list("Smugaski")
        assert len(result) == 2
        assert isinstance(result[0], ChartDateRange)
