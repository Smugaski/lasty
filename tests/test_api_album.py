"""Tests for AlbumAPI — mocked HTTP responses."""

from __future__ import annotations

import pytest

from lasty.api.album import AlbumAPI
from lasty.models.album import AlbumInfo, AlbumSearchResult
from lasty.models.tag import Tag, TopTag

from tests.conftest import BASE_URL_REGEX


@pytest.fixture
def album_api(http_client_no_secret):
    return AlbumAPI(http_client_no_secret)


class TestAlbumGetInfo:
    @pytest.mark.asyncio
    async def test_get_info(self, album_api, mock_aiohttp):
        mock_aiohttp.get(
            BASE_URL_REGEX,
            payload={
                "album": {
                    "name": "Mutter",
                    "mbid": "",
                    "url": "url",
                    "artist": "Rammstein",
                    "listeners": "5000",
                    "playcount": "20000",
                    "tracks": {"track": []},
                    "tags": {"tag": []},
                    "image": [],
                }
            },
        )
        result = await album_api.get_info("Rammstein", "Mutter")
        assert isinstance(result, AlbumInfo)
        assert result.name == "Mutter"
        assert result.listeners == 5000


class TestAlbumGetTags:
    @pytest.mark.asyncio
    async def test_get_tags(self, album_api, mock_aiohttp):
        mock_aiohttp.get(
            BASE_URL_REGEX,
            payload={"tags": {"tag": [{"name": "industrial metal", "url": "url"}]}},
        )
        result = await album_api.get_tags("Rammstein", "Mutter", "Smugaski")
        assert len(result) == 1
        assert isinstance(result[0], Tag)

    @pytest.mark.asyncio
    async def test_get_tags_empty(self, album_api, mock_aiohttp):
        mock_aiohttp.get(
            BASE_URL_REGEX,
            payload={"tags": {}},
        )
        result = await album_api.get_tags("Rammstein", "Mutter", "Smugaski")
        assert result == []


class TestAlbumGetTopTags:
    @pytest.mark.asyncio
    async def test_get_top_tags(self, album_api, mock_aiohttp):
        mock_aiohttp.get(
            BASE_URL_REGEX,
            payload={
                "toptags": {
                    "tag": [{"name": "industrial metal", "url": "url", "count": "100"}]
                }
            },
        )
        result = await album_api.get_top_tags("Rammstein", "Mutter")
        assert len(result) == 1
        assert isinstance(result[0], TopTag)


class TestAlbumSearch:
    @pytest.mark.asyncio
    async def test_search(self, album_api, mock_aiohttp):
        mock_aiohttp.get(
            BASE_URL_REGEX,
            payload={
                "results": {
                    "opensearch:totalResults": "50",
                    "opensearch:startIndex": "0",
                    "opensearch:itemsPerPage": "30",
                    "albummatches": {
                        "album": [
                            {
                                "name": "Mutter",
                                "mbid": "",
                                "url": "url",
                                "artist": "Rammstein",
                                "image": [],
                                "streamable": "0",
                            }
                        ]
                    },
                }
            },
        )
        result = await album_api.search("Mutter")
        assert len(result.items) == 1
        assert isinstance(result.items[0], AlbumSearchResult)
        assert result.attr.total == 50
