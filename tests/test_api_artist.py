"""Tests for ArtistAPI — mocked HTTP responses."""

from __future__ import annotations

import pytest

from lasty.api.artist import ArtistAPI
from lasty.models.artist import ArtistInfo, ArtistCorrection, SimilarArtist, TopArtist
from lasty.models.album import TopAlbum
from lasty.models.track import TopTrack
from lasty.models.tag import Tag, TopTag

from tests.conftest import BASE_URL_REGEX


@pytest.fixture
def artist_api(http_client_no_secret):
    return ArtistAPI(http_client_no_secret)


class TestArtistGetInfo:
    @pytest.mark.asyncio
    async def test_get_info(self, artist_api, mock_aiohttp):
        mock_aiohttp.get(
            BASE_URL_REGEX,
            payload={
                "artist": {
                    "name": "Rammstein",
                    "mbid": "abc",
                    "url": "url",
                    "streamable": "0",
                    "ontour": "0",
                    "stats": {"listeners": "1000", "playcount": "5000"},
                    "similar": {"artist": []},
                    "tags": {"tag": []},
                    "image": [],
                }
            },
        )
        result = await artist_api.get_info("Rammstein")
        assert isinstance(result, ArtistInfo)
        assert result.name == "Rammstein"


class TestArtistGetCorrection:
    @pytest.mark.asyncio
    async def test_get_correction(self, artist_api, mock_aiohttp):
        mock_aiohttp.get(
            BASE_URL_REGEX,
            payload={
                "corrections": {
                    "correction": {
                        "artist": {"name": "Linkin Park", "mbid": "", "url": "url"}
                    }
                }
            },
        )
        result = await artist_api.get_correction("linkin park")
        assert isinstance(result, ArtistCorrection)
        assert result.artist.name == "Linkin Park"


class TestArtistGetSimilar:
    @pytest.mark.asyncio
    async def test_get_similar(self, artist_api, mock_aiohttp):
        mock_aiohttp.get(
            BASE_URL_REGEX,
            payload={
                "similarartists": {
                    "artist": [
                        {
                            "name": "Linkin Park",
                            "mbid": "",
                            "url": "url",
                            "match": "0.85",
                            "image": [],
                        }
                    ],
                }
            },
        )
        result = await artist_api.get_similar("Rammstein")
        assert len(result) == 1
        assert isinstance(result[0], SimilarArtist)
        assert result[0].match == 0.85


class TestArtistGetTags:
    @pytest.mark.asyncio
    async def test_get_tags(self, artist_api, mock_aiohttp):
        mock_aiohttp.get(
            BASE_URL_REGEX,
            payload={"tags": {"tag": [{"name": "industrial metal", "url": "url"}]}},
        )
        result = await artist_api.get_tags("Rammstein", "Smugaski")
        assert len(result) == 1
        assert isinstance(result[0], Tag)


class TestArtistGetTopAlbums:
    @pytest.mark.asyncio
    async def test_get_top_albums(self, artist_api, mock_aiohttp):
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
        result = await artist_api.get_top_albums("Rammstein")
        assert len(result.items) == 1
        assert isinstance(result.items[0], TopAlbum)


class TestArtistGetTopTags:
    @pytest.mark.asyncio
    async def test_get_top_tags(self, artist_api, mock_aiohttp):
        mock_aiohttp.get(
            BASE_URL_REGEX,
            payload={
                "toptags": {
                    "tag": [{"name": "industrial metal", "url": "url", "count": "100"}]
                }
            },
        )
        result = await artist_api.get_top_tags("Rammstein")
        assert len(result) == 1
        assert isinstance(result[0], TopTag)


class TestArtistGetTopTracks:
    @pytest.mark.asyncio
    async def test_get_top_tracks(self, artist_api, mock_aiohttp):
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
        result = await artist_api.get_top_tracks("Rammstein")
        assert len(result.items) == 1
        assert isinstance(result.items[0], TopTrack)


class TestArtistSearch:
    @pytest.mark.asyncio
    async def test_search(self, artist_api, mock_aiohttp):
        mock_aiohttp.get(
            BASE_URL_REGEX,
            payload={
                "results": {
                    "opensearch:totalResults": "100",
                    "opensearch:startIndex": "0",
                    "opensearch:itemsPerPage": "30",
                    "artistmatches": {
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
                        ]
                    },
                }
            },
        )
        result = await artist_api.search("Rammstein")
        assert len(result.items) == 1
        assert isinstance(result.items[0], TopArtist)
