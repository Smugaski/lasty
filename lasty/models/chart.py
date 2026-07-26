"""Chart and weekly-chart models.

Contains shared structures for weekly chart metadata and date ranges.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Generic, TypeVar

from .._types import JSONDict

__all__ = [
    "WeeklyChartAttr",
    "WeeklyChart",
    "ChartDateRange",
]

T = TypeVar("T")


@dataclass(frozen=True, slots=True)
class WeeklyChartAttr:
    """Metadata for a weekly chart response.

    Attributes:
        user: The username the chart belongs to.
        from_date: Start of the chart period (UNIX timestamp).
        to_date: End of the chart period (UNIX timestamp).
    """

    user: str
    from_date: int
    to_date: int

    @classmethod
    def from_data(cls, data: JSONDict | None) -> WeeklyChartAttr:
        """Parse weekly chart attributes.

        Args:
            data: The ``@attr`` dict from a weekly chart response.
        """
        if not data:
            return cls(user="", from_date=0, to_date=0)
        return cls(
            user=data.get("user", ""),
            from_date=int(data.get("from", 0)),
            to_date=int(data.get("to", 0)),
        )


@dataclass(frozen=True, slots=True)
class WeeklyChart(Generic[T]):
    """A generic weekly chart containing items and time-range metadata.

    Attributes:
        items: The chart entries for the period.
        attr: Chart period metadata (user, from, to).
    """

    items: list[T]
    attr: WeeklyChartAttr


@dataclass(frozen=True, slots=True)
class ChartDateRange:
    """A date range from ``user.getWeeklyChartList``.

    Attributes:
        from_date: Start of the chart period (UNIX timestamp).
        to_date: End of the chart period (UNIX timestamp).
    """

    from_date: int
    to_date: int

    @classmethod
    def from_data(cls, data: JSONDict) -> ChartDateRange:
        """Parse a chart date range.

        Args:
            data: A dict with ``from`` and ``to`` keys.
        """
        return cls(
            from_date=int(data.get("from", 0)),
            to_date=int(data.get("to", 0)),
        )
