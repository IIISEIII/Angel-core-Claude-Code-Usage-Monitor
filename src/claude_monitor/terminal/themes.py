"""Unified theme management for terminal display."""

import logging
import os
import re
import sys
import threading
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple, Union

# Windows-compatible imports with graceful fallbacks
try:
    import select
    import termios
    import tty

    HAS_TERMIOS: bool = True
except ImportError:
    HAS_TERMIOS: bool = False

from rich.console import Console
from rich.theme import Theme


class BackgroundType(Enum):
    """Background detection types."""

    LIGHT = "light"
    DARK = "dark"
    UNKNOWN = "unknown"


@dataclass
class ThemeConfig:
    """Theme configuration for terminal display.

    Attributes:
        name: Human-readable theme name.
        colors: Mapping of color keys to ANSI/hex color values.
        symbols: Unicode symbols and ASCII fallbacks for theme.
        rich_theme: Rich library theme configuration.
    """

    name: str
    colors: Dict[str, str]
    symbols: Dict[str, Union[str, List[str]]]
    rich_theme: Theme

    def get_color(self, key: str, default: str = "default") -> str:
        """Get color for key with fallback.

        Args:
            key: Color key to look up.
            default: Default color value if key not found.

        Returns:
            Color value string (ANSI code, hex, or color name).
        """
        return self.colors.get(key, default)


class AdaptiveColorScheme:
    """Scientifically-based adaptive color schemes with proper contrast ratios.

    IMPORTANT: This only changes FONT/FOREGROUND colors, never background colors.
    The terminal's background remains unchanged - we adapt text colors for readability.

    All color choices follow WCAG AA accessibility standards for contrast ratios.
    """

    @staticmethod
    def get_light_background_theme() -> Theme:
        """Angelcore palette, tuned for light terminal backgrounds."""
        return Theme(
            {
                "header": "#77709F",  # lavender
                "info": "#557C9C",  # blue
                "warning": "#927B48",  # yellow
                "error": "#AE6677",  # rose
                "success": "#5F856B",  # green
                "value": "#3F3E4A",  # foreground
                "dim": "#8A8B98",  # muted
                "separator": "#8A8B98",  # muted
                "progress_bar": "#675D91",  # purple
                "highlight": "#AE6677",  # rose - matches error
                # Cost styles
                "cost.low": "#675D91",  # purple - uniform fill, tier shown by icon only
                "cost.medium": "#675D91",  # purple - uniform fill, tier shown by icon only
                "cost.high": "#675D91",  # purple - uniform fill, tier shown by icon only
                # Table styles
                "table.border": "#8A8B98",  # muted
                "table.header": "bold #77709F",  # bold lavender
                "table.row": "#3F3E4A",  # foreground
                "table.row.alt": "#6F7284",  # soft_text
                # Progress styles
                "progress.bar.fill": "#675D91",  # purple
                "progress.bar": "#675D91",  # purple (fallback)
                "progress.bar.empty": "#D3D2D8",  # surface_lavender x muted
                "progress.percentage": "bold #3F3E4A",  # bold foreground
                # Chart styles
                "chart.bar": "#557C9C",  # blue
                "chart.line": "#4F8D91",  # cyan
                "chart.point": "#AE6677",  # rose
                "chart.axis": "#8A8B98",  # muted
                "chart.label": "#3F3E4A",  # foreground
                # Status styles
                "status.active": "#5F856B",  # green
                "status.inactive": "#8A8B98",  # muted
                "status.warning": "#927B48",  # yellow
                "status.error": "#AE6677",  # rose
                # Time styles
                "time.elapsed": "#3F3E4A",  # foreground
                "time.remaining": "#927B48",  # yellow
                "time.duration": "#557C9C",  # blue
                # Model styles
                "model.opus": "#77709F",  # lavender
                "model.sonnet": "#557C9C",  # blue
                "model.haiku": "#5F856B",  # green
                "model.unknown": "#8A8B98",  # muted
                # Plan styles
                "plan.pro": "#A66F87",  # pink (premium)
                "plan.max5": "#557C9C",  # blue
                "plan.max20": "#77709F",  # lavender
                "plan.custom": "#5F856B",  # green
            }
        )

    @staticmethod
    def get_dark_background_theme() -> Theme:
        """Angelcore palette, lightened for dark terminal backgrounds."""
        return Theme(
            {
                "header": "#A7A2C1",  # lavender, lightened
                "info": "#90AABF",  # blue, lightened
                "warning": "#B8A988",  # yellow, lightened
                "error": "#CA9CA7",  # rose, lightened
                "success": "#97B09F",  # green, lightened
                "value": "#D5D5D7",  # foreground, lightened
                "dim": "#B3B4BC",  # muted, lightened
                "separator": "#B3B4BC",  # muted, lightened
                "progress_bar": "#9C96B8",  # purple, lightened
                "highlight": "#CA9CA7",  # rose - matches error
                # Cost styles
                "cost.low": "#9C96B8",  # purple, lightened - uniform fill, tier shown by icon only
                "cost.medium": "#9C96B8",  # purple, lightened - uniform fill, tier shown by icon only
                "cost.high": "#9C96B8",  # purple, lightened - uniform fill, tier shown by icon only
                # Table styles
                "table.border": "#B3B4BC",  # muted, lightened
                "table.header": "bold #A7A2C1",  # bold lavender, lightened
                "table.row": "#D5D5D7",  # foreground, lightened
                "table.row.alt": "#A1A3AF",  # soft_text, lightened
                # Progress styles
                "progress.bar.fill": "#9C96B8",  # purple, lightened
                "progress.bar": "#9C96B8",  # purple, lightened (fallback)
                "progress.bar.empty": "#6F6E77",  # foreground, subtly lightened
                "progress.percentage": "bold #D5D5D7",  # bold foreground, lightened
                # Chart styles
                "chart.bar": "#90AABF",  # blue, lightened
                "chart.line": "#8DB5B8",  # cyan, lightened
                "chart.point": "#CA9CA7",  # rose, lightened
                "chart.axis": "#B3B4BC",  # muted, lightened
                "chart.label": "#D5D5D7",  # foreground, lightened
                # Status styles
                "status.active": "#97B09F",  # green, lightened
                "status.inactive": "#B3B4BC",  # muted, lightened
                "status.warning": "#B8A988",  # yellow, lightened
                "status.error": "#CA9CA7",  # rose, lightened
                # Time styles
                "time.elapsed": "#D5D5D7",  # foreground, lightened
                "time.remaining": "#B8A988",  # yellow, lightened
                "time.duration": "#90AABF",  # blue, lightened
                # Model styles
                "model.opus": "#A7A2C1",  # lavender, lightened
                "model.sonnet": "#90AABF",  # blue, lightened
                "model.haiku": "#97B09F",  # green, lightened
                "model.unknown": "#B3B4BC",  # muted, lightened
                # Plan styles
                "plan.pro": "#C5A1B1",  # pink, lightened (premium)
                "plan.max5": "#90AABF",  # blue, lightened
                "plan.max20": "#A7A2C1",  # lavender, lightened
                "plan.custom": "#97B09F",  # green, lightened
            }
        )

    @staticmethod
    def get_classic_theme() -> Theme:
        """Classic colors for maximum compatibility."""
        return Theme(
            {
                "header": "cyan",
                "info": "blue",
                "warning": "yellow",
                "error": "red",
                "success": "green",
                "value": "white",
                "dim": "bright_black",
                "separator": "white",
                "progress_bar": "green",
                "highlight": "red",
                # Cost styles
                "cost.low": "green",
                "cost.medium": "yellow",
                "cost.high": "red",
                # Table styles
                "table.border": "white",
                "table.header": "bold cyan",
                "table.row": "white",
                "table.row.alt": "bright_black",
                # Progress styles
                "progress.bar.fill": "green",
                "progress.bar.empty": "bright_black",
                "progress.percentage": "bold white",
                # Chart styles
                "chart.bar": "blue",
                "chart.line": "cyan",
                "chart.point": "red",
                "chart.axis": "white",
                "chart.label": "white",
                # Status styles
                "status.active": "green",
                "status.inactive": "bright_black",
                "status.warning": "yellow",
                "status.error": "red",
                # Time styles
                "time.elapsed": "white",
                "time.remaining": "yellow",
                "time.duration": "blue",
                # Model styles
                "model.opus": "cyan",
                "model.sonnet": "blue",
                "model.haiku": "green",
                "model.unknown": "bright_black",
                # Plan styles
                "plan.pro": "yellow",  # Yellow (premium)
                "plan.max5": "cyan",  # Cyan
                "plan.max20": "blue",  # Blue
                "plan.custom": "green",  # Green
            }
        )


class BackgroundDetector:
    """Detects terminal background type using multiple methods.

    Uses environment variables, OSC queries, and heuristics to determine
    whether the terminal has a light or dark background for optimal theming.
    """

    @staticmethod
    def detect_background() -> BackgroundType:
        """Detect terminal background using multiple methods.

        Tries multiple detection methods in order of reliability:
        1. COLORFGBG environment variable
        2. Known terminal environment hints
        3. OSC 11 color query (advanced terminals)

        Returns:
            Detected background type, defaults to DARK if unknown.
        """
        # Method 1: Check COLORFGBG environment variable
        colorfgbg_result: BackgroundType = BackgroundDetector._check_colorfgbg()
        if colorfgbg_result != BackgroundType.UNKNOWN:
            return colorfgbg_result

        # Method 2: Check known terminal environment variables
        env_result: BackgroundType = BackgroundDetector._check_environment_hints()
        if env_result != BackgroundType.UNKNOWN:
            return env_result

        # Method 3: Use OSC 11 query (advanced terminals only)
        osc_result: BackgroundType = BackgroundDetector._query_background_color()
        if osc_result != BackgroundType.UNKNOWN:
            return osc_result

        # Default fallback
        return BackgroundType.DARK

    @staticmethod
    def _check_colorfgbg() -> BackgroundType:
        """Check COLORFGBG environment variable.

        COLORFGBG format: "foreground;background" where background
        color 0-7 indicates dark, 8-15 indicates light background.

        Returns:
            Background type based on COLORFGBG or UNKNOWN if unavailable.
        """
        colorfgbg: str = os.environ.get("COLORFGBG", "")
        if not colorfgbg:
            return BackgroundType.UNKNOWN

        try:
            # COLORFGBG format: "foreground;background"
            parts: List[str] = colorfgbg.split(";")
            if len(parts) >= 2:
                bg_color: int = int(parts[-1])
                # Colors 0-7 are typically dark, 8-15 are bright
                return BackgroundType.LIGHT if bg_color >= 8 else BackgroundType.DARK
        except (ValueError, IndexError) as e:
            # COLORFGBG parsing failed - not critical, will use other detection methods
            logger: logging.Logger = logging.getLogger(__name__)
            logger.debug(f"Failed to parse COLORFGBG '{colorfgbg}': {e}")

        return BackgroundType.UNKNOWN

    @staticmethod
    def _check_environment_hints() -> BackgroundType:
        """Check environment variables for theme hints.

        Checks known terminal-specific environment variables and patterns
        to infer the likely background type.

        Returns:
            Background type based on environment hints or UNKNOWN.
        """
        # Windows Terminal session
        if os.environ.get("WT_SESSION"):
            return BackgroundType.DARK

        # Check terminal program
        if "TERM_PROGRAM" in os.environ:
            term_program: str = os.environ["TERM_PROGRAM"]
            if term_program == "Apple_Terminal":
                return BackgroundType.LIGHT
            if term_program == "iTerm.app":
                return BackgroundType.DARK

        # Check TERM variable patterns
        term: str = os.environ.get("TERM", "").lower()
        if "light" in term:
            return BackgroundType.LIGHT
        if "dark" in term:
            return BackgroundType.DARK

        return BackgroundType.UNKNOWN

    @staticmethod
    def _query_background_color() -> BackgroundType:
        """Query terminal background color using OSC 11.

        Sends an OSC (Operating System Command) 11 query to request the terminal's
        background color, then calculates perceived brightness to determine if
        the background is light or dark.

        Returns:
            Background type based on OSC 11 response or UNKNOWN if query fails.
        """
        if not HAS_TERMIOS:
            return BackgroundType.UNKNOWN

        if not sys.stdin.isatty() or not sys.stdout.isatty():
            return BackgroundType.UNKNOWN

        old_settings: Optional[List[Any]] = None
        try:
            # Save terminal settings
            old_settings = termios.tcgetattr(sys.stdin)

            # Set terminal to raw mode
            tty.setraw(sys.stdin.fileno())

            # Send OSC 11 query
            sys.stdout.write("\033]11;?\033\\")
            sys.stdout.flush()

            # Wait for response with timeout
            ready_streams: List[Any] = select.select([sys.stdin], [], [], 0.1)[0]
            if ready_streams:
                # Read available data without blocking
                response: str = ""
                try:
                    # Read character by character with timeout to avoid blocking
                    import fcntl
                    import os

                    # Set stdin to non-blocking mode
                    fd = sys.stdin.fileno()
                    fl = fcntl.fcntl(fd, fcntl.F_GETFL)
                    fcntl.fcntl(fd, fcntl.F_SETFL, fl | os.O_NONBLOCK)

                    # Read up to 50 chars with timeout
                    for _ in range(50):
                        ready = select.select([sys.stdin], [], [], 0.01)[0]
                        if not ready:
                            break
                        char = sys.stdin.read(1)
                        if not char:
                            break
                        response += char
                        # Stop if we get the expected terminator
                        if response.endswith("\033\\"):
                            break

                    # Restore blocking mode
                    fcntl.fcntl(fd, fcntl.F_SETFL, fl)

                except (OSError, ImportError):
                    # Fallback to simple read if fcntl is not available
                    response = sys.stdin.read(50)

                # Parse response: \033]11;rgb:rrrr/gggg/bbbb\033\\
                if response:  # Only proceed if we got a response
                    rgb_match = re.search(
                        r"rgb:([0-9a-f]+)/([0-9a-f]+)/([0-9a-f]+)", response
                    )
                    if rgb_match:
                        r: str
                        g: str
                        b: str
                        r, g, b = rgb_match.groups()
                        # Convert hex to int and calculate brightness
                        red: int = int(r[:2], 16) if len(r) >= 2 else 0
                        green: int = int(g[:2], 16) if len(g) >= 2 else 0
                        blue: int = int(b[:2], 16) if len(b) >= 2 else 0

                        # Calculate perceived brightness using standard formula
                        brightness: float = (
                            red * 299 + green * 587 + blue * 114
                        ) / 1000

                        # Restore terminal settings
                        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)

                        return (
                            BackgroundType.LIGHT
                            if brightness > 127
                            else BackgroundType.DARK
                        )

            # Restore terminal settings
            if old_settings is not None:
                termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)

        except (OSError, termios.error, AttributeError):
            # Restore terminal settings on any error
            if old_settings is not None:
                try:
                    termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)
                except (OSError, termios.error, AttributeError) as e:
                    # Terminal settings restoration failed - log but continue
                    # This is non-critical as the terminal will be cleaned up on process exit
                    logger: logging.Logger = logging.getLogger(__name__)
                    logger.warning(
                        f"Failed to restore terminal settings during OSC query: {e}"
                    )

        return BackgroundType.UNKNOWN


class ThemeManager:
    """Manages themes with auto-detection and thread safety."""

    def __init__(self):
        self._lock = threading.Lock()
        self._current_theme: Optional[ThemeConfig] = None
        self._forced_theme: Optional[str] = None
        self.themes = self._load_themes()

    def _load_themes(self) -> Dict[str, ThemeConfig]:
        """Load all available themes.

        Creates theme configurations for light, dark, and classic themes
        with appropriate Rich theme objects and symbol sets.

        Returns:
            Dictionary mapping theme names to ThemeConfig objects.
        """
        themes: Dict[str, ThemeConfig] = {}

        # Load themes with Rich theme objects
        light_rich: Theme = AdaptiveColorScheme.get_light_background_theme()
        dark_rich: Theme = AdaptiveColorScheme.get_dark_background_theme()
        classic_rich: Theme = AdaptiveColorScheme.get_classic_theme()

        themes["light"] = ThemeConfig(
            name="light",
            colors={},  # No longer using color mappings from defaults.py
            symbols=self._get_symbols_for_theme("light"),
            rich_theme=light_rich,
        )

        themes["dark"] = ThemeConfig(
            name="dark",
            colors={},  # No longer using color mappings from defaults.py
            symbols=self._get_symbols_for_theme("dark"),
            rich_theme=dark_rich,
        )

        themes["classic"] = ThemeConfig(
            name="classic",
            colors={},  # No longer using color mappings from defaults.py
            symbols=self._get_symbols_for_theme("classic"),
            rich_theme=classic_rich,
        )

        return themes

    def _get_symbols_for_theme(
        self, theme_name: str
    ) -> Dict[str, Union[str, List[str]]]:
        """Get symbols based on theme.

        Args:
            theme_name: Name of theme to get symbols for.

        Returns:
            Dictionary mapping symbol names to Unicode or ASCII characters.
            Spinner symbols are returned as a list for animation.
        """
        if theme_name == "classic":
            return {
                "progress_empty": "-",
                "progress_full": "#",
                "bullet": "*",
                "arrow": "->",
                "check": "[OK]",
                "cross": "[X]",
                "spinner": ["|", "/", "-", "\\"],
            }
        return {
            "progress_empty": "░",
            "progress_full": "█",
            "bullet": "•",
            "arrow": "→",
            "check": "✓",
            "cross": "✗",
            "spinner": ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"],
        }

    def auto_detect_theme(self) -> str:
        """Auto-detect appropriate theme based on terminal.

        Uses BackgroundDetector to determine terminal background
        and returns appropriate theme name.

        Returns:
            Theme name ('light', 'dark') based on detected background.
            Defaults to 'dark' if detection fails.
        """
        background: BackgroundType = BackgroundDetector.detect_background()

        if background == BackgroundType.LIGHT:
            return "light"
        if background == BackgroundType.DARK:
            return "dark"
        # Default to dark if unknown
        return "dark"

    def get_theme(
        self, name: Optional[str] = None, force_detection: bool = False
    ) -> ThemeConfig:
        """Get theme by name or auto-detect.

        Args:
            name: Theme name ('light', 'dark', 'classic', 'auto') or None for auto.
            force_detection: Force re-detection of terminal background.

        Returns:
            ThemeConfig object for the requested or detected theme.
        """
        with self._lock:
            if name == "auto" or name is None:
                if force_detection or self._forced_theme is None:
                    detected_name: str = self.auto_detect_theme()
                    theme: ThemeConfig = self.themes.get(
                        detected_name, self.themes["dark"]
                    )
                    if not force_detection:
                        self._forced_theme = detected_name
                else:
                    theme = self.themes.get(self._forced_theme, self.themes["dark"])
            else:
                theme = self.themes.get(name, self.themes["dark"])
                self._forced_theme = name if name in self.themes else None

            self._current_theme = theme
            return theme

    def get_console(
        self, theme_name: Optional[str] = None, force_detection: bool = False
    ) -> Console:
        """Get themed console instance.

        Args:
            theme_name: Theme name or None for auto-detection.
            force_detection: Force re-detection of terminal background.

        Returns:
            Rich Console instance configured with the selected theme.
        """
        theme: ThemeConfig = self.get_theme(theme_name, force_detection)
        return Console(theme=theme.rich_theme, force_terminal=True)

    def get_current_theme(self) -> Optional[ThemeConfig]:
        """Get currently active theme.

        Returns:
            Currently active ThemeConfig or None if no theme selected.
        """
        return self._current_theme


# Cost-based styles with thresholds (moved from ui/styles.py)
COST_STYLES: Dict[str, str] = {
    "low": "cost.low",  # Green - costs under $1
    "medium": "cost.medium",  # Yellow - costs $1-$10
    "high": "cost.high",  # Red - costs over $10
}

# Cost thresholds for automatic style selection
COST_THRESHOLDS: List[Tuple[float, str]] = [
    (10.0, COST_STYLES["high"]),
    (1.0, COST_STYLES["medium"]),
    (0.0, COST_STYLES["low"]),
]

# Velocity/burn rate emojis and labels
VELOCITY_INDICATORS: Dict[str, Dict[str, Union[str, float]]] = {
    "slow": {"emoji": "🐌", "label": "Slow", "threshold": 50},
    "normal": {"emoji": "➡️", "label": "Normal", "threshold": 150},
    "fast": {"emoji": "🚀", "label": "Fast", "threshold": 300},
    "very_fast": {"emoji": "⚡", "label": "Very fast", "threshold": float("inf")},
}


# Helper functions for style selection
def get_cost_style(cost: float) -> str:
    """Get appropriate style for a cost value.

    Args:
        cost: Cost value in USD to categorize.

    Returns:
        Rich style name for the cost category.
    """
    for threshold, style in COST_THRESHOLDS:
        if cost >= threshold:
            return style
    return COST_STYLES["low"]


def get_velocity_indicator(burn_rate: float) -> Dict[str, str]:
    """Get velocity indicator based on burn rate.

    Args:
        burn_rate: Token consumption rate (tokens per minute).

    Returns:
        Dictionary with 'emoji' and 'label' keys for the velocity category.
    """
    for indicator in VELOCITY_INDICATORS.values():
        threshold_value = indicator["threshold"]
        if isinstance(threshold_value, (int, float)) and burn_rate < threshold_value:
            return {"emoji": str(indicator["emoji"]), "label": str(indicator["label"])}
    very_fast = VELOCITY_INDICATORS["very_fast"]
    return {"emoji": str(very_fast["emoji"]), "label": str(very_fast["label"])}


# Global theme manager instance
_theme_manager: ThemeManager = ThemeManager()


def get_theme(name: Optional[str] = None) -> Theme:
    """Get Rich theme by name or auto-detect.

    Args:
        name: Theme name ('light', 'dark', 'classic') or None for auto-detection

    Returns:
        Rich Theme object
    """
    theme_config = _theme_manager.get_theme(name)
    return theme_config.rich_theme


def get_themed_console(force_theme: Optional[Union[str, bool]] = None) -> Console:
    """Get themed console - backward compatibility wrapper.

    Args:
        force_theme: Theme name to force, or None for auto-detection.

    Returns:
        Rich Console instance with appropriate theme.
    """
    if force_theme and isinstance(force_theme, str):
        return _theme_manager.get_console(force_theme)
    return _theme_manager.get_console(None)


def print_themed(text: str, style: str = "info") -> None:
    """Print text with themed styling - backward compatibility.

    Args:
        text: Text to print with styling.
        style: Rich style name to apply.
    """
    console: Console = _theme_manager.get_console()
    console.print(f"[{style}]{text}[/]")
