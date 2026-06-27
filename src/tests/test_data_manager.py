"""Tests for monitoring data manager wiring."""

from unittest.mock import Mock, patch

from claude_monitor.monitoring.data_manager import DataManager


@patch("claude_monitor.monitoring.data_manager.analyze_usage")
def test_data_manager_passes_warehouse_options_to_analysis(mock_analyze: Mock) -> None:
    """Live refreshes honor opt-in warehouse persistence settings."""
    mock_analyze.return_value = {"blocks": []}
    manager = DataManager(
        cache_ttl=0,
        hours_back=24,
        data_path=["/profiles/a"],
        filter_models="all",
        write_warehouse=True,
        warehouse_file="/tmp/usage.json",
        warehouse_retention_days=30,
    )

    assert manager.get_data(force_refresh=True) == {"blocks": []}

    mock_analyze.assert_called_once_with(
        hours_back=24,
        quick_start=False,
        use_cache=False,
        data_path=["/profiles/a"],
        filter_models="all",
        write_warehouse=True,
        warehouse_file="/tmp/usage.json",
        warehouse_retention_days=30,
    )
