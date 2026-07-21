# lasty

**A fully typed, modern, and asynchronous Python client for the Last.fm API.**

[![Python Version](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://python.org)
[![Asyncio](https://img.shields.io/badge/asyncio-supported-brightgreen.svg)](https://docs.python.org/3/library/asyncio.html)
[![Type Checked](https://img.shields.io/badge/mypy-strict-informational.svg)](http://mypy-lang.org/)
[![License](https://img.shields.io/badge/license-Apache%202.0-purple.svg)](LICENSE)

---

**lasty** is an asynchronous Python library for interacting with the Last.fm API. Built on top of `aiohttp`, it provides clean abstractions, robust error handling, auto-pagination, and complete static typing (`mypy --strict`).

## Features

- **Asynchronous**: Built natively on `aiohttp` for non-blocking HTTP requests.
- **Strictly Typed**: Every endpoint, payload, and response is backed by typed frozen dataclasses.
- **API Mirroring**: Namespaces match the official Last.fm API hierarchy (e.g. `client.user.get_info()`).
- **Error Handling**: Dedicated exception hierarchy mapped directly to Last.fm error codes.
- **Automatic Retries**: Exponential backoff for rate limits (HTTP 429) and temporary server errors (HTTP 5xx).
- **Auto-Pagination**: `iter_*` helpers to asynchronously stream through paginated endpoints.
- **Request Signing**: Automatic MD5 signature generation for write operations like scrobbling.

## Installation

```bash
pip install lasty
```

Requires Python 3.10 or higher.

## Quick Start

```python
import asyncio
from lasty import LastFM, Period

async def main():
    async with LastFM(api_key="your_api_key") as client:
        # Fetch user information
        user = await client.user.get_info("Smugaski")
        print(f"User: {user.name} | Total Scrobbles: {user.playcount}")

        # Fetch recent tracks
        recent = await client.user.get_recent_tracks("Smugaski", limit=5)
        for track in recent.items:
            if track.now_playing:
                print(f"Now playing: {track.artist_name} - {track.name}")
            else:
                date_str = track.date.text if track.date else 'unknown'
                print(f"Played: {track.artist_name} - {track.name} at {date_str}")

if __name__ == "__main__":
    asyncio.run(main())
```

## Core Concepts

### API Namespaces
The `lasty` client exposes namespaced sub-clients matching the official Last.fm API documentation:

- `client.user` (e.g. `.get_info()`, `.get_recent_tracks()`, `.get_top_artists()`)
- `client.artist` (e.g. `.get_info()`, `.get_similar()`, `.search()`)
- `client.album` (e.g. `.get_info()`, `.search()`, `.add_tags()`)
- `client.track` (e.g. `.get_info()`, `.scrobble()`, `.love()`)
- `client.tag` (e.g. `.get_info()`, `.get_top_tracks()`)
- `client.chart` (e.g. `.get_top_artists()`, `.get_top_tracks()`)
- `client.geo` (e.g. `.get_top_artists("Poland")`)
- `client.library` (e.g. `.get_artists()`)
- `client.auth` (e.g. `.get_token()`, `.get_session()`)

### Pagination & Iterators
For endpoints returning paginated lists, `lasty` offers `iter_*` companion methods returning `AsyncIterator` instances:

```python
import asyncio
from lasty import LastFM, Period

async def get_top_artists():
    async with LastFM(api_key="your_api_key") as client:
        async for artist in client.user.iter_top_artists("Smugaski", period=Period.SEVEN_DAY, limit=50, max_items=200):
            print(f"Artist: {artist.name} (Playcount: {artist.playcount})")
```

### Authenticated Write Operations
Write operations (such as scrobbling or loving a track) require `api_secret` and a user `session_key`. `lasty` handles request signing automatically.

```python
import asyncio
import time
from lasty import LastFM

async def auth_examples():
    async with LastFM(
        api_key="your_api_key", 
        api_secret="your_api_secret", 
        session_key="user_session_key"
    ) as client:
        
        # Love a track
        await client.track.love("Rammstein", "Sonne")
        
        # Scrobble a track
        result = await client.track.scrobble(
            artist="Rammstein",
            track="Sonne",
            timestamp=int(time.time()),
        )
        print(f"Scrobble result: {result.accepted} accepted, {result.ignored} ignored.")
```

### Authentication Flow
To acquire a user `session_key`:

```python
async with LastFM(api_key="key", api_secret="secret") as client:
    token = await client.auth.get_token()
    auth_url = client.auth.get_auth_url(token)
    print(f"Authorize the application at: {auth_url}")
    input("Press Enter after authorizing...")
    
    session = await client.auth.get_session(token)
    print(f"Session Key: {session.key}")
    print(f"User: {session.name}")
```

### Error Handling
API errors raise typed exceptions inheriting from `LastFMError`:

```python
from lasty import LastFM
from lasty.errors import InvalidParametersError, RateLimitError

async def handle_errors():
    async with LastFM(api_key="your_api_key") as client:
        try:
            await client.user.get_info("nonexistent_user_123456789")
        except InvalidParametersError as e:
            print(f"User not found: {e}")
        except RateLimitError:
            print("Rate limit exceeded.")
```

## Development

Install development dependencies and the package in editable mode:

```bash
pip install -e .[dev]
```

Run tests and type checks:

```bash
python -m pytest tests/
mypy lasty --strict
```

## License

This project is licensed under the Apache 2.0 License.
