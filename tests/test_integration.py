"""Live integration tests against the real Last.fm API.

These tests are SKIPPED by default unless the LASTFM_API_KEY environment
variable is set. Run them with:

    LASTFM_API_KEY=your_key pytest tests/test_integration.py -v

They only use read-only (GET) endpoints, so no session key is needed.
"""

from __future__ import annotations

import os

import pytest
import pytest_asyncio

from lasty import LastFM
from lasty.models.user import UserInfo
from lasty.models.artist import ArtistInfo
from lasty.models.album import AlbumInfo
from lasty.models.track import TrackInfo
from lasty.models.tag import TagInfo

API_KEY = os.environ.get("LASTFM_API_KEY")
pytestmark = pytest.mark.skipif(
    not API_KEY,
    reason="LASTFM_API_KEY not set — skipping live integration tests",
)


@pytest_asyncio.fixture
async def client():
    """Provide a real LastFM client for integration testing."""
    async with LastFM(api_key=API_KEY) as c:
        yield c


@pytest.mark.asyncio
async def test_user_get_info(client):
    """Test user.getInfo against the live API."""
    result = await client.user.get_info("Smugaski")
    assert isinstance(result, UserInfo)
    assert result.name.lower() == "smugaski"
    assert result.playcount > 0


@pytest.mark.asyncio
async def test_artist_get_info(client):
    """Test artist.getInfo against the live API."""
    result = await client.artist.get_info("Rammstein")
    assert isinstance(result, ArtistInfo)
    assert result.name == "Rammstein"


@pytest.mark.asyncio
async def test_album_get_info(client):
    """Test album.getInfo against the live API."""
    result = await client.album.get_info("Rammstein", "Mutter")
    assert isinstance(result, AlbumInfo)
    assert result.name == "Mutter"
    assert result.listeners > 0


@pytest.mark.asyncio
async def test_track_get_info(client):
    """Test track.getInfo against the live API."""
    result = await client.track.get_info("Rammstein", "Du Hast")
    assert isinstance(result, TrackInfo)
    assert result.name == "Du Hast"


@pytest.mark.asyncio
async def test_tag_get_info(client):
    """Test tag.getInfo against the live API."""
    result = await client.tag.get_info("rock")
    assert isinstance(result, TagInfo)
    assert result.name == "rock"


@pytest.mark.asyncio
async def test_user_get_recent_tracks(client):
    """Test user.getRecentTracks against the live API."""
    result = await client.user.get_recent_tracks("Smugaski", limit=5)
    assert len(result.items) > 0
    assert result.attr.total > 0


@pytest.mark.asyncio
async def test_chart_get_top_artists(client):
    """Test chart.getTopArtists against the live API."""
    result = await client.chart.get_top_artists(limit=5)
    assert len(result.items) > 0


@pytest.mark.asyncio
async def test_geo_get_top_artists(client):
    """Test geo.getTopArtists against the live API."""
    result = await client.geo.get_top_artists("Poland", limit=5)
    assert len(result.items) > 0
