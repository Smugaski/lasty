"""Tests for lasty.auth — MD5 signature generation."""

from __future__ import annotations

import hashlib

from lasty.auth import generate_signature


class TestGenerateSignature:
    """Tests for generate_signature()."""

    def test_basic_signature(self):
        """Verify deterministic MD5 output for known input."""
        params = {
            "api_key": "MYKEY",
            "method": "auth.getSession",
            "token": "MYTOKEN",
        }
        secret = "MYSECRET"
        result = generate_signature(params, secret)

        expected_input = "api_keyMYKEYmethodauth.getSessiontokenMYTOKENMYSECRET"
        expected = hashlib.md5(expected_input.encode("utf-8")).hexdigest().upper()
        assert result == expected

    def test_format_is_excluded(self):
        """The 'format' key must be excluded from the signature."""
        params = {
            "api_key": "KEY",
            "format": "json",
            "method": "user.getInfo",
        }
        secret = "SEC"
        result = generate_signature(params, secret)

        expected_input = "api_keyKEYmethoduser.getInfoSEC"
        expected = hashlib.md5(expected_input.encode("utf-8")).hexdigest().upper()
        assert result == expected

    def test_alphabetical_sort(self):
        """Parameters must be sorted alphabetically by key."""
        params_a = {"z_param": "z", "a_param": "a", "m_param": "m"}
        params_b = {"a_param": "a", "m_param": "m", "z_param": "z"}
        secret = "SECRET"
        assert generate_signature(params_a, secret) == generate_signature(
            params_b, secret
        )

    def test_empty_params(self):
        """Signature with empty params should just hash the secret."""
        result = generate_signature({}, "SECRET")
        expected = hashlib.md5("SECRET".encode("utf-8")).hexdigest().upper()
        assert result == expected

    def test_result_is_32_char_hex(self):
        """Output must be a 32-character uppercase hex string."""
        result = generate_signature({"key": "val"}, "secret")
        assert len(result) == 32
        assert result == result.upper()
        int(result, 16)

    def test_unicode_values(self):
        """Signature generation must handle Unicode values correctly."""
        params = {"artist": "Rammstein", "method": "artist.getInfo"}
        secret = "SEC"
        result = generate_signature(params, secret)
        expected_input = "artistRammsteinmethodartist.getInfoSEC"
        expected = hashlib.md5(expected_input.encode("utf-8")).hexdigest().upper()
        assert result == expected
