"""Tests for all model from_data parsers across every model file."""

from __future__ import annotations

from lasty.enums import ImageSize
from lasty.models.common import (
    Image,
    Wiki,
    DateInfo,
    Streamable,
    PaginationAttr,
)
from lasty.models.artist import (
    BaseArtist,
    ArtistSummary,
    SimilarArtist,
    TopArtist,
    WeeklyChartArtist,
    LibraryArtist,
    ArtistStats,
    ArtistBio,
    ArtistInfo,
    ArtistCorrection,
)
from lasty.models.album import (
    BaseAlbum,
    TrackAlbum,
    TopAlbum,
    WeeklyChartAlbum,
    AlbumTrack,
    AlbumInfo,
)
from lasty.models.track import (
    BaseTrack,
    TopTrack,
    LovedTrack,
    RecentTrack,
    WeeklyChartTrack,
    SimilarTrack,
    TrackInfo,
    TrackCorrection,
    ScrobbleResult,
    NowPlayingResult,
)
from lasty.models.user import BaseUser, UserInfo, Friend
from lasty.models.tag import Tag, TopTag, UserTag, TagInfo
from lasty.models.chart import WeeklyChartAttr, ChartDateRange


class TestImage:
    def test_from_data(self):
        data = {"#text": "https://img.fm/pic.jpg", "size": "large"}
        img = Image.from_data(data)
        assert img.url == "https://img.fm/pic.jpg"
        assert img.size == ImageSize.LARGE

    def test_unknown_size(self):
        data = {"#text": "url", "size": "supermega"}
        img = Image.from_data(data)
        assert img.size == ImageSize.UNKNOWN

    def test_empty_size(self):
        data = {"#text": "url", "size": ""}
        img = Image.from_data(data)
        assert img.size == ImageSize.UNKNOWN

    def test_list_from_data_none(self):
        assert Image.list_from_data(None) == []

    def test_list_from_data_empty(self):
        assert Image.list_from_data([]) == []

    def test_list_from_data_multiple(self):
        data = [
            {"#text": "a.jpg", "size": "small"},
            {"#text": "b.jpg", "size": "medium"},
        ]
        images = Image.list_from_data(data)
        assert len(images) == 2
        assert images[0].size == ImageSize.SMALL
        assert images[1].size == ImageSize.MEDIUM


class TestWiki:
    def test_from_data(self):
        data = {
            "published": "06 Oct 2008",
            "summary": "Short text",
            "content": "Full text",
        }
        wiki = Wiki.from_data(data)
        assert wiki is not None
        assert wiki.published == "06 Oct 2008"
        assert wiki.summary == "Short text"
        assert wiki.content == "Full text"

    def test_from_data_none(self):
        assert Wiki.from_data(None) is None

    def test_from_data_empty_dict(self):
        assert Wiki.from_data({}) is None


class TestDateInfo:
    def test_from_data(self):
        data = {"uts": "1603187000", "#text": "20 Oct 2020, 10:03"}
        d = DateInfo.from_data(data)
        assert d is not None
        assert d.uts == 1603187000
        assert d.text == "20 Oct 2020, 10:03"

    def test_from_data_none(self):
        assert DateInfo.from_data(None) is None


class TestStreamable:
    def test_from_dict(self):
        data = {"fulltrack": "1", "#text": "1"}
        s = Streamable.from_data(data)
        assert s is not None
        assert s.fulltrack == "1"
        assert s.text == "1"

    def test_from_string(self):
        s = Streamable.from_data("0")
        assert s is not None
        assert s.fulltrack == "0"
        assert s.text == "0"

    def test_from_none(self):
        assert Streamable.from_data(None) is None


class TestPaginationAttr:
    def test_from_data(self):
        data = {"page": "3", "perPage": "25", "total": "500", "totalPages": "20", "user": "Smugaski"}
        attr = PaginationAttr.from_data(data)
        assert attr.page == 3
        assert attr.per_page == 25
        assert attr.total == 500
        assert attr.total_pages == 20
        assert attr.user == "Smugaski"

    def test_from_none(self):
        attr = PaginationAttr.from_data(None)
        assert attr.page == 1
        assert attr.per_page == 50
        assert attr.total == 0
        assert attr.total_pages == 0

    def test_from_empty_dict(self):
        attr = PaginationAttr.from_data({})
        assert attr.page == 1


class TestBaseArtist:
    def test_from_data(self):
        data = {"name": "Rammstein", "mbid": "abc123", "url": "https://last.fm/music/Rammstein"}
        a = BaseArtist.from_data(data)
        assert a.name == "Rammstein"
        assert a.mbid == "abc123"
        assert a.url == "https://last.fm/music/Rammstein"

    def test_missing_fields(self):
        a = BaseArtist.from_data({})
        assert a.name == ""
        assert a.mbid == ""
        assert a.url == ""


class TestArtistSummary:
    def test_from_data(self):
        data = {
            "name": "Rammstein",
            "mbid": "abc",
            "url": "https://last.fm/music/Rammstein",
            "playcount": "12345",
            "listeners": "6789",
            "streamable": "0",
            "image": [{"#text": "img.jpg", "size": "small"}],
        }
        a = ArtistSummary.from_data(data)
        assert a.playcount == 12345
        assert a.listeners == 6789
        assert len(a.images) == 1


class TestSimilarArtist:
    def test_from_data(self):
        data = {
            "name": "Linkin Park",
            "mbid": "def",
            "url": "url",
            "match": "0.85",
            "image": [],
        }
        a = SimilarArtist.from_data(data)
        assert a.match == 0.85


class TestTopArtist:
    def test_from_data(self):
        data = {
            "name": "Rammstein",
            "mbid": "abc",
            "url": "url",
            "playcount": "500",
            "@attr": {"rank": "1"},
            "streamable": "0",
            "image": [],
        }
        a = TopArtist.from_data(data)
        assert a.playcount == 500
        assert a.rank == 1


class TestWeeklyChartArtist:
    def test_from_data(self):
        data = {
            "name": "Rammstein",
            "mbid": "",
            "url": "url",
            "playcount": "42",
            "@attr": {"rank": "3"},
        }
        a = WeeklyChartArtist.from_data(data)
        assert a.playcount == 42
        assert a.rank == 3


class TestLibraryArtist:
    def test_from_data(self):
        data = {
            "name": "Rammstein",
            "mbid": "",
            "url": "url",
            "playcount": "100",
            "tagcount": "5",
            "streamable": "0",
            "image": [],
        }
        a = LibraryArtist.from_data(data)
        assert a.playcount == 100
        assert a.tagcount == 5


class TestArtistStats:
    def test_from_data(self):
        data = {"listeners": "1000", "playcount": "5000", "userplaycount": "50"}
        s = ArtistStats.from_data(data)
        assert s is not None
        assert s.listeners == 1000
        assert s.playcount == 5000
        assert s.userplaycount == 50

    def test_from_none(self):
        assert ArtistStats.from_data(None) is None

    def test_without_userplaycount(self):
        data = {"listeners": "1000", "playcount": "5000"}
        s = ArtistStats.from_data(data)
        assert s is not None
        assert s.userplaycount is None


class TestArtistBio:
    def test_from_data(self):
        data = {
            "published": "01 Jan 2020",
            "summary": "Short bio",
            "content": "Full bio",
            "links": {"link": {"href": "https://wiki.example.com"}},
        }
        bio = ArtistBio.from_data(data)
        assert bio is not None
        assert bio.link_url == "https://wiki.example.com"

    def test_from_none(self):
        assert ArtistBio.from_data(None) is None


class TestArtistInfo:
    def test_from_data(self):
        data = {
            "name": "Rammstein",
            "mbid": "abc",
            "url": "url",
            "streamable": "0",
            "ontour": "0",
            "stats": {"listeners": "1000", "playcount": "5000"},
            "similar": {"artist": [{"name": "Linkin Park", "mbid": "", "url": "url", "image": []}]},
            "tags": {"tag": [{"name": "industrial metal", "url": "tagurl"}]},
            "bio": {"published": "date", "summary": "s", "content": "c"},
            "image": [],
        }
        info = ArtistInfo.from_data(data)
        assert info.name == "Rammstein"
        assert info.stats is not None
        assert info.stats.listeners == 1000
        assert len(info.similar) == 1
        assert len(info.tags) == 1
        assert info.tags[0].name == "industrial metal"
        assert info.bio is not None


class TestArtistCorrection:
    def test_from_data(self):
        data = {
            "corrections": {
                "correction": {
                    "artist": {"name": "Linkin Park", "mbid": "abc", "url": "url"}
                }
            }
        }
        c = ArtistCorrection.from_data(data)
        assert c.artist.name == "Linkin Park"


class TestBaseAlbum:
    def test_from_data_string_artist(self):
        data = {"name": "Mutter", "mbid": "", "url": "url", "artist": "Rammstein"}
        a = BaseAlbum.from_data(data)
        assert a.name == "Mutter"
        assert a.artist == "Rammstein"

    def test_from_data_dict_artist(self):
        data = {"name": "Mutter", "mbid": "", "url": "url", "artist": {"name": "Rammstein"}}
        a = BaseAlbum.from_data(data)
        assert a.artist == "Rammstein"

    def test_title_fallback(self):
        data = {"title": "Sehnsucht", "mbid": "", "url": "url", "artist": "Rammstein"}
        a = BaseAlbum.from_data(data)
        assert a.name == "Sehnsucht"


class TestTrackAlbum:
    def test_from_data(self):
        data = {
            "artist": "Rammstein",
            "title": "Mutter",
            "mbid": "",
            "url": "url",
            "image": [{"#text": "img.jpg", "size": "large"}],
            "@attr": {"position": "3"},
        }
        a = TrackAlbum.from_data(data)
        assert a is not None
        assert a.title == "Mutter"
        assert a.position == 3

    def test_from_none(self):
        assert TrackAlbum.from_data(None) is None


class TestTopAlbum:
    def test_from_data(self):
        data = {
            "name": "Mutter",
            "mbid": "",
            "url": "url",
            "artist": {"name": "Rammstein", "mbid": "", "url": "url2"},
            "playcount": "999",
            "@attr": {"rank": "1"},
            "image": [],
        }
        a = TopAlbum.from_data(data)
        assert a.playcount == 999
        assert a.rank == 1
        assert a.artist == "Rammstein"
        assert a.artist_obj is not None


class TestWeeklyChartAlbum:
    def test_from_data(self):
        data = {
            "name": "Mutter",
            "mbid": "",
            "url": "url",
            "artist": {"#text": "Rammstein"},
            "playcount": "50",
            "@attr": {"rank": "2"},
        }
        a = WeeklyChartAlbum.from_data(data)
        assert a.artist == "Rammstein"
        assert a.rank == 2


class TestAlbumTrack:
    def test_from_data(self):
        data = {
            "name": "Sonne",
            "url": "url",
            "duration": "290",
            "@attr": {"rank": "1"},
            "streamable": {"fulltrack": "0", "#text": "0"},
            "artist": {"name": "Rammstein", "mbid": "", "url": "url"},
        }
        t = AlbumTrack.from_data(data)
        assert t.name == "Sonne"
        assert t.duration == 290
        assert t.rank == 1
        assert t.artist is not None


class TestAlbumInfo:
    def test_from_data(self):
        data = {
            "name": "Mutter",
            "mbid": "",
            "url": "url",
            "artist": "Rammstein",
            "listeners": "5000",
            "playcount": "20000",
            "tracks": {
                "track": [
                    {
                        "name": "Sonne",
                        "url": "url",
                        "duration": "290",
                        "@attr": {"rank": "1"},
                    }
                ]
            },
            "tags": {"tag": [{"name": "industrial metal", "url": "tagurl"}]},
            "wiki": {"published": "date", "summary": "s", "content": "c"},
            "image": [],
            "userplaycount": "10",
        }
        info = AlbumInfo.from_data(data)
        assert info.listeners == 5000
        assert len(info.tracks) == 1
        assert len(info.tags) == 1
        assert info.wiki is not None
        assert info.userplaycount == 10


class TestBaseTrack:
    def test_from_data_dict_artist(self):
        data = {
            "name": "Du Hast",
            "mbid": "",
            "url": "url",
            "artist": {"name": "Rammstein", "mbid": "", "url": "url"},
        }
        t = BaseTrack.from_data(data)
        assert t.artist_name == "Rammstein"
        assert t.artist is not None

    def test_from_data_string_artist(self):
        data = {"name": "Du Hast", "mbid": "", "url": "url", "artist": "Rammstein"}
        t = BaseTrack.from_data(data)
        assert t.artist_name == "Rammstein"
        assert t.artist is None

    def test_from_data_text_artist(self):
        """Handle the #text format used in recent tracks."""
        data = {"name": "Du Hast", "mbid": "", "url": "url", "artist": {"#text": "Rammstein"}}
        t = BaseTrack.from_data(data)
        assert t.artist_name == "Rammstein"
        assert t.artist is None


class TestTopTrack:
    def test_from_data(self):
        data = {
            "name": "Du Hast",
            "mbid": "",
            "url": "url",
            "artist": {"name": "Rammstein", "mbid": "", "url": "url"},
            "playcount": "777",
            "@attr": {"rank": "2"},
            "duration": "240",
            "image": [],
        }
        t = TopTrack.from_data(data)
        assert t.playcount == 777
        assert t.rank == 2
        assert t.duration == 240


class TestLovedTrack:
    def test_from_data(self):
        data = {
            "name": "Du Hast",
            "mbid": "",
            "url": "url",
            "artist": {"name": "Rammstein", "mbid": "", "url": "url"},
            "date": {"uts": "1603187000", "#text": "20 Oct 2020"},
            "image": [],
        }
        t = LovedTrack.from_data(data)
        assert t.date is not None
        assert t.date.uts == 1603187000


class TestRecentTrack:
    def test_standard_format(self):
        data = {
            "name": "Du Hast",
            "mbid": "",
            "url": "url",
            "artist": {"#text": "Rammstein", "mbid": ""},
            "album": {"#text": "Sehnsucht", "mbid": ""},
            "image": [],
            "date": {"uts": "1603187000", "#text": "20 Oct 2020"},
            "streamable": "0",
        }
        t = RecentTrack.from_data(data)
        assert t.artist_name == "Rammstein"
        assert t.album_name == "Sehnsucht"
        assert not t.now_playing

    def test_now_playing(self):
        data = {
            "name": "Du Hast",
            "mbid": "",
            "url": "url",
            "artist": {"#text": "Rammstein", "mbid": ""},
            "album": {"#text": "Sehnsucht", "mbid": ""},
            "@attr": {"nowplaying": "true"},
            "image": [],
            "streamable": "0",
        }
        t = RecentTrack.from_data(data)
        assert t.now_playing is True
        assert t.date is None


class TestWeeklyChartTrack:
    def test_from_data(self):
        data = {
            "name": "Du Hast",
            "mbid": "",
            "url": "url",
            "artist": {"#text": "Rammstein"},
            "playcount": "15",
            "@attr": {"rank": "5"},
            "image": [],
        }
        t = WeeklyChartTrack.from_data(data)
        assert t.playcount == 15
        assert t.rank == 5
        assert t.artist_name == "Rammstein"


class TestSimilarTrack:
    def test_from_data(self):
        data = {
            "name": "Sonne",
            "mbid": "",
            "url": "url",
            "artist": {"name": "Rammstein", "mbid": "", "url": "url"},
            "match": "0.95",
            "duration": "380",
            "playcount": "1000",
            "image": [],
        }
        t = SimilarTrack.from_data(data)
        assert t.match == 0.95
        assert t.duration == 380


class TestTrackInfo:
    def test_from_data(self):
        data = {
            "name": "Du Hast",
            "mbid": "",
            "url": "url",
            "artist": {"name": "Rammstein", "mbid": "", "url": "url"},
            "duration": "240000",
            "listeners": "5000",
            "playcount": "20000",
            "streamable": {"fulltrack": "0", "#text": "0"},
            "album": {
                "artist": "Rammstein",
                "title": "Sehnsucht",
                "mbid": "",
                "url": "url",
            },
            "toptags": {"tag": [{"name": "industrial metal", "url": "tagurl"}]},
            "wiki": {"published": "date", "summary": "s", "content": "c"},
            "userplaycount": "10",
            "userloved": "1",
        }
        info = TrackInfo.from_data(data)
        assert info.duration == 240000
        assert info.listeners == 5000
        assert len(info.toptags) == 1
        assert info.album is not None
        assert info.userplaycount == 10
        assert info.userloved == "1"


class TestTrackCorrection:
    def test_from_data(self):
        data = {
            "corrections": {
                "correction": {
                    "track": {"name": "Du Hast", "mbid": "", "url": "url", "artist": "Rammstein"}
                }
            }
        }
        c = TrackCorrection.from_data(data)
        assert c.track.name == "Du Hast"


class TestScrobbleResult:
    def test_from_data(self):
        data = {"scrobbles": {"@attr": {"accepted": "1", "ignored": "0"}}}
        r = ScrobbleResult.from_data(data)
        assert r.accepted == 1
        assert r.ignored == 0


class TestNowPlayingResult:
    def test_from_data(self):
        data = {
            "nowplaying": {
                "artist": {"#text": "Rammstein", "corrected": "0"},
                "track": {"#text": "Du Hast", "corrected": "0"},
                "album": {"#text": "Sehnsucht", "corrected": "0"},
                "ignoredMessage": {"#text": "", "code": "0"},
            }
        }
        r = NowPlayingResult.from_data(data)
        assert r.artist == "Rammstein"
        assert r.track == "Du Hast"
        assert r.album == "Sehnsucht"


class TestBaseUser:
    def test_from_data(self):
        data = {"name": "Smugaski", "url": "https://last.fm/user/Smugaski"}
        u = BaseUser.from_data(data)
        assert u.name == "Smugaski"


class TestUserInfo:
    def test_from_data(self):
        data = {
            "name": "Smugaski",
            "url": "https://last.fm/user/Smugaski",
            "playcount": "100000",
            "playlists": "5",
            "image": [],
            "registered": {"uts": "1000000", "#text": "date"},
            "country": "PL",
            "age": "30",
            "gender": "m",
            "subscriber": "1",
            "realname": "Smugaski",
            "type": "user",
            "bootstrap": "0",
        }
        u = UserInfo.from_data(data)
        assert u.playcount == 100000
        assert u.country == "PL"
        assert u.subscriber == "1"


class TestFriend:
    def test_from_data(self):
        data = {
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
        f = Friend.from_data(data)
        assert f.name == "friend1"
        assert f.playcount == 5000


class TestTag:
    def test_from_data(self):
        data = {"name": "industrial metal", "url": "https://last.fm/tag/industrial+metal"}
        t = Tag.from_data(data)
        assert t.name == "industrial metal"


class TestTopTag:
    def test_from_data(self):
        data = {"name": "industrial metal", "url": "url", "count": "100"}
        t = TopTag.from_data(data)
        assert t.count == 100


class TestUserTag:
    def test_from_data(self):
        data = {"name": "industrial metal", "url": "url", "count": "50"}
        t = UserTag.from_data(data)
        assert t.count == 50


class TestTagInfo:
    def test_from_data(self):
        data = {
            "name": "rock",
            "url": "url",
            "total": "1000",
            "reach": "500",
            "wiki": {"published": "date", "summary": "s", "content": "c"},
        }
        t = TagInfo.from_data(data)
        assert t.total == 1000
        assert t.reach == 500
        assert t.wiki is not None


class TestWeeklyChartAttr:
    def test_from_data(self):
        data = {"user": "Smugaski", "from": "1000000", "to": "1600000"}
        a = WeeklyChartAttr.from_data(data)
        assert a.user == "Smugaski"
        assert a.from_date == 1000000
        assert a.to_date == 1600000

    def test_from_none(self):
        a = WeeklyChartAttr.from_data(None)
        assert a.user == ""
        assert a.from_date == 0


class TestChartDateRange:
    def test_from_data(self):
        data = {"from": "1000000", "to": "1600000"}
        r = ChartDateRange.from_data(data)
        assert r.from_date == 1000000
        assert r.to_date == 1600000
