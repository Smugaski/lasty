"""Tests for the LastFM client lifecycle and HTTPClient internals."""

from __future__ import annotations

import pytest

from lasty.client import LastFM
from lasty.http import HTTPClient


class TestHTTPClientLifecycle:
    """Test HTTPClient session management."""

    @pytest.mark.asyncio
    async def test_ensure_session_raises_before_start(self):
        """_ensure_session should raise RuntimeError if not started."""
        client = HTTPClient(api_key="test")
        with pytest.raises(RuntimeError, match="not started"):
            client._ensure_session()

    @pytest.mark.asyncio
    async def test_start_creates_session(self):
        """start() should create an aiohttp.ClientSession."""
        client = HTTPClient(api_key="test")
        await client.start()
        try:
            session = client._ensure_session()
            assert session is not None
            assert not session.closed
        finally:
            await client.close()

    @pytest.mark.asyncio
    async def test_close_cleans_up(self):
        """close() should close the session and set it to None."""
        client = HTTPClient(api_key="test")
        await client.start()
        await client.close()
        assert client._session is None

    @pytest.mark.asyncio
    async def test_double_start(self):
        """Calling start() twice should not create a second session."""
        client = HTTPClient(api_key="test")
        await client.start()
        session1 = client._session
        await client.start()
        session2 = client._session
        assert session1 is session2
        await client.close()

    @pytest.mark.asyncio
    async def test_close_without_start(self):
        """Closing a never-started client should not raise."""
        client = HTTPClient(api_key="test")
        await client.close()  # Should not raise


class TestLastFMContextManager:
    """Test the LastFM async context manager."""

    @pytest.mark.asyncio
    async def test_context_manager(self):
        """async with LastFM should start and then close the session."""
        async with LastFM(api_key="test") as client:
            # Session should be active
            session = client._http._ensure_session()
            assert not session.closed

        # After exiting, session should be closed
        assert client._http._session is None

    @pytest.mark.asyncio
    async def test_cached_properties(self):
        """API namespace properties should return consistent instances."""
        async with LastFM(api_key="test") as client:
            assert client.user is client.user
            assert client.artist is client.artist
            assert client.album is client.album
            assert client.track is client.track
            assert client.tag is client.tag
            assert client.chart is client.chart
            assert client.geo is client.geo
            assert client.library is client.library
            assert client.auth is client.auth

    @pytest.mark.asyncio
    async def test_custom_user_agent(self):
        """Custom user_agent should be used in session headers."""
        async with LastFM(api_key="test", user_agent="MyApp/1.0") as client:
            session = client._http._ensure_session()
            assert session.headers.get("User-Agent") == "MyApp/1.0"
