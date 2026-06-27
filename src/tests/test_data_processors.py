"""Tests for TimestampProcessor (epoch parsing correctness)."""

from datetime import datetime, timezone

from claude_monitor.core.data_processors import TimestampProcessor


def test_epoch_parsed_as_utc_not_local_wall_time() -> None:
    """An integer epoch is an absolute instant and must be interpreted as UTC,
    regardless of the host timezone (issues #106, #114, #220)."""
    epoch = 1782579600  # 2026-06-27T17:00:00Z
    expected = datetime.fromtimestamp(epoch, tz=timezone.utc)

    result = TimestampProcessor().parse_timestamp(epoch)

    # Equality on aware datetimes compares the absolute instant; on a non-UTC
    # host the old local-wall-time parse was off by the host offset.
    assert result == expected
    assert result.utcoffset() == timezone.utc.utcoffset(None)


def test_float_epoch_parsed_as_utc() -> None:
    epoch = 1782579600.0
    assert TimestampProcessor().parse_timestamp(epoch) == datetime.fromtimestamp(
        epoch, tz=timezone.utc
    )
