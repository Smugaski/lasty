"""Tests for AuthAPI — mocked HTTP responses."""

from __future__ import annotations

import pytest

from lasty.api.auth import AuthAPI, Session

from tests.conftest import API_KEY, BASE_URL_REGEX


@pytest.fixture
def auth_api(http_client):
    return AuthAPI(http_client)


class TestAuthGetToken:
    @pytest.mark.asyncio
    async def test_get_token(self, auth_api, mock_aiohttp):
        mock_aiohttp.post(
            BASE_URL_REGEX,
            payload={"token": "abc123token"},
        )
        result = await auth_api.get_token()
        assert result == "abc123token"


class TestAuthGetSession:
    @pytest.mark.asyncio
    async def test_get_session(self, auth_api, mock_aiohttp):
        mock_aiohttp.post(
            BASE_URL_REGEX,
            payload={
                "session": {
                    "name": "testuser",
                    "key": "sk_12345",
                    "subscriber": "0",
                }
            },
        )
        result = await auth_api.get_session("abc123token")
        assert isinstance(result, Session)
        assert result.name == "testuser"
        assert result.key == "sk_12345"


class TestAuthGetAuthUrl:
    def test_get_auth_url(self, http_client):
        auth = AuthAPI(http_client)
        token = "mytoken"
        url = auth.get_auth_url(token)
        assert API_KEY in url
        assert token in url
        assert url.startswith("https://www.last.fm/api/auth/")


class TestSession:
    def test_from_data(self):
        data = {"name": "user1", "key": "sk_test", "subscriber": "1"}
        s = Session.from_data(data)
        assert s.name == "user1"
        assert s.key == "sk_test"
        assert s.subscriber == "1"

    def test_from_data_defaults(self):
        s = Session.from_data({})
        assert s.name == ""
        assert s.key == ""
        assert s.subscriber == "0"
