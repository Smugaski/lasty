"""Tests for lasty.errors — exception hierarchy and from_response."""

from __future__ import annotations

from lasty.errors import (
    LastFMError,
    ServiceUnavailableError,
    InvalidMethodError,
    AuthenticationFailedError,
    InvalidFormatError,
    InvalidParametersError,
    InvalidResourceError,
    OperationFailedError,
    InvalidSessionError,
    InvalidAPIKeyError,
    ServiceOfflineError,
    InvalidMethodSignatureError,
    TemporaryError,
    LoginRequiredError,
    SuspendedAPIKeyError,
    RateLimitError,
    _ERROR_CODE_MAP,
)


class TestErrorCodeMap:
    """Test the error code → exception class mapping."""

    def test_all_known_codes_are_registered(self):
        """Verify every known error code has a registered subclass."""
        expected = {
            2: ServiceUnavailableError,
            3: InvalidMethodError,
            4: AuthenticationFailedError,
            5: InvalidFormatError,
            6: InvalidParametersError,
            7: InvalidResourceError,
            8: OperationFailedError,
            9: InvalidSessionError,
            10: InvalidAPIKeyError,
            11: ServiceOfflineError,
            13: InvalidMethodSignatureError,
            16: TemporaryError,
            17: LoginRequiredError,
            26: SuspendedAPIKeyError,
            29: RateLimitError,
        }
        for code, cls in expected.items():
            assert _ERROR_CODE_MAP[code] is cls, f"Code {code} not mapped to {cls.__name__}"

    def test_class_code_attribute(self):
        """Each subclass should have its code set as a class attribute."""
        assert InvalidAPIKeyError.code == 10
        assert RateLimitError.code == 29
        assert TemporaryError.code == 16


class TestFromResponse:
    """Test LastFMError.from_response() factory."""

    def test_known_error_code(self):
        """Should return the correct subclass for a known error code."""
        data = {"error": 10, "message": "Invalid API Key"}
        error = LastFMError.from_response(data)
        assert isinstance(error, InvalidAPIKeyError)
        assert error.code == 10
        assert error.message == "Invalid API Key"

    def test_unknown_error_code(self):
        """Should return base LastFMError for unknown codes."""
        data = {"error": 999, "message": "Unknown error"}
        error = LastFMError.from_response(data)
        assert type(error) is LastFMError
        assert error.code == 999

    def test_string_error_code(self):
        """Should handle error codes as strings (API sometimes returns these)."""
        data = {"error": "6", "message": "Invalid parameters"}
        error = LastFMError.from_response(data)
        assert isinstance(error, InvalidParametersError)
        assert error.code == 6

    def test_missing_error_key(self):
        """Should default to code 0 if 'error' key is missing."""
        data = {"message": "Something went wrong"}
        error = LastFMError.from_response(data)
        assert error.code == 0

    def test_missing_message_key(self):
        """Should default to 'Unknown error' if 'message' key is missing."""
        data = {"error": 3}
        error = LastFMError.from_response(data)
        assert isinstance(error, InvalidMethodError)
        assert error.message == "Unknown error"

    def test_str_representation(self):
        """Error string should include code and message."""
        error = LastFMError("test message", 42)
        assert "[Error 42]" in str(error)
        assert "test message" in str(error)

    def test_inheritance_chain(self):
        """All error subclasses should be subclasses of LastFMError and Exception."""
        assert issubclass(RateLimitError, LastFMError)
        assert issubclass(RateLimitError, Exception)
        assert issubclass(InvalidAPIKeyError, LastFMError)
