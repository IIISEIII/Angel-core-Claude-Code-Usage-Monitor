"""Live rich TUI uses the same official-aware snapshot as machine outputs."""

import argparse
import importlib
from pathlib import Path
from typing import Any
from unittest.mock import MagicMock, Mock, patch

import pytest

from claude_monitor.output.snapshots import build_snapshot
from claude_monitor.ui.display_controller import DisplayController
from claude_monitor.ui.session_display import SessionDisplayComponent

cli_main = importlib.import_module("claude_monitor.cli.main")


def _payload(total: int = 12008) -> dict[str, Any]:
    return {
        "token_limit": 19000,
        "data": {
            "blocks": [
                {
                    "id": "b1",
                    "isActive": True,
                    "isGap": False,
                    "startTime": "2026-06-27T12:00:00+00:00",
                    "endTime": "2026-06-27T17:00:00+00:00",
                    "durationMinutes": 300,
                    "tokenCounts": {
                        "inputTokens": 8500,
                        "outputTokens": 3508,
                        "cacheCreationInputTokens": 5000,
                        "cacheReadInputTokens": 2000,
                    },
                    "totalTokens": total,
                    "costUSD": 4.27,
                    "sentMessagesCount": 42,
                    "burnRate": {"tokensPerMinute": 40.0, "costPerHour": 1.31},
                }
            ]
        },
    }


def _official_limits() -> dict[str, Any]:
    return {
        "five_hour": {
            "used_percentage": 42.5,
            "resets_at": "2026-06-27T17:00:00+00:00",
            "resets_at_epoch": 1782579600,
            "stale": False,
        }
    }


def _args() -> argparse.Namespace:
    return argparse.Namespace(
        view="realtime",
        theme="dark",
        plan="pro",
        timezone="UTC",
        time_format="24h",
        refresh_per_second=1.0,
        refresh_rate=10,
        compact=False,
        write_state=False,
        set_terminal_title=False,
        custom_limit_tokens=None,
        hide_model_distribution=False,
        no_header=True,
        no_emoji=False,
        api=False,
    )


def test_live_rich_tui_receives_official_snapshot_without_machine_consumers() -> None:
    """Normal interactive TUI must not skip the official-aware snapshot."""

    class LiveOrchestrator:
        def __init__(self, **_: Any) -> None:
            self.callback = None

        def set_args(self, _args: argparse.Namespace) -> None:
            pass

        def register_update_callback(self, callback: Any) -> None:
            self.callback = callback

        def register_session_callback(self, _callback: Any) -> None:
            pass

        def start(self) -> None:
            assert self.callback is not None
            self.callback(_payload())

        def wait_for_initial_data(self, timeout: float) -> bool:
            return True

        def stop(self) -> None:
            pass

    live_display = MagicMock()
    display_controller = Mock()
    display_controller.live_manager.create_live_display.return_value = live_display
    display_controller.create_loading_display.return_value = "loading"
    display_controller.create_data_display.return_value = "display"

    with (
        patch.object(cli_main, "discover_claude_data_paths", return_value=[Path("/x")]),
        patch.object(cli_main, "_get_initial_token_limit", return_value=19000),
        patch.object(cli_main, "get_themed_console", return_value=Mock()),
        patch.object(cli_main, "setup_terminal", return_value=None),
        patch.object(cli_main, "enter_alternate_screen"),
        patch.object(cli_main, "restore_terminal"),
        patch.object(cli_main, "DisplayController", return_value=display_controller),
        patch.object(cli_main, "MonitoringOrchestrator", LiveOrchestrator),
        patch.object(cli_main, "read_official_limits", return_value=_official_limits()),
        patch.object(cli_main.signal, "pause", side_effect=KeyboardInterrupt),
        patch.object(cli_main, "handle_cleanup_and_exit", side_effect=SystemExit(0)),
    ):
        with pytest.raises(SystemExit):
            cli_main._run_monitoring(_args())

    snapshot = display_controller.create_data_display.call_args.kwargs["snapshot"]
    five = snapshot["limits"]["five_hour"]
    assert five["confidence"] == "official"
    assert five["used_percentage"] == 42.5


def test_display_controller_uses_official_snapshot_percentage_for_token_bar() -> None:
    args = _args()
    payload = _payload()
    snapshot = build_snapshot(
        payload["data"], args, payload["token_limit"], official=_official_limits()
    )

    with patch("claude_monitor.ui.display_controller.NotificationManager"):
        controller = DisplayController()

    with (
        patch.object(
            controller.session_display, "format_active_session_screen"
        ) as mock_format,
        patch.object(
            controller.buffer_manager, "create_screen_renderable"
        ) as mock_render,
    ):
        mock_format.return_value = ["screen"]
        mock_render.return_value = "rendered"

        result = controller.create_data_display(
            payload["data"], args, payload["token_limit"], snapshot=snapshot
        )

    assert result == "rendered"
    rendered_kwargs = mock_format.call_args.kwargs
    assert rendered_kwargs["usage_percentage"] == 42.5
    assert rendered_kwargs["limit_confidence"] == "official"


def test_no_active_screen_uses_official_snapshot_percentage() -> None:
    args = _args()
    snapshot = build_snapshot({"blocks": []}, args, 19000, official=_official_limits())

    lines = SessionDisplayComponent().format_no_active_session_screen(
        plan="pro",
        timezone="UTC",
        token_limit=19000,
        current_time=None,
        args=args,
        snapshot=snapshot,
    )
    joined = "\n".join(lines)

    assert "42.5%" in joined
    assert "(official)" in joined
    assert "--" in next(line for line in lines if "Tokens:" in line)
