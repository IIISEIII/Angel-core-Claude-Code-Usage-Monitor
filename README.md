# ISEI's Angel Core Claude Usage Monitor Customize

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![日本語](https://img.shields.io/badge/日本語-README-blue.svg)](README.ja.md)

A personal fork of [**Maciek-roboblog/Claude-Code-Usage-Monitor**](https://github.com/Maciek-roboblog/Claude-Code-Usage-Monitor) — all credit for the original tool, its architecture, and its feature set goes to **Maciek** ([@Maciek-roboblog](https://github.com/Maciek-roboblog)). This fork does not add features; it rethemes and reshapes the terminal dashboard to a personal taste ("Angelcore" — soft, muted, pastel) and fixes one rendering bug found along the way. The full original README is preserved at [README.upstream.md](README.upstream.md), and the original `LICENSE` (MIT) is unchanged.

If you just want the upstream tool, go use the original repo — it's actively maintained and this fork will drift from it. This repo exists to document a specific personal setup (an "Angelcore"-themed, ultra-compact iTerm2 dashboard) in case it's useful or interesting to anyone else doing the same kind of customization.

![Dashboard](doc/angelcore-dashboard.png)

---

## What's different from upstream

Everything below is layered on top of upstream `claude-monitor` v4.0.0. Three source files were edited (see `git diff` against the `upstream/main` branch, or the sections below); four new setup scripts were added under [`macos-setup/`](macos-setup/).

### 1. Angelcore color theme

`src/claude_monitor/terminal/themes.py` — both the light- and dark-background `Theme` tables were rewritten to a muted, low-saturation "Angelcore" palette instead of the upstream xterm-256 palette:

| Role | Hex | Used for |
|---|---|---|
| `foreground` | `#3F3E4A` | primary text |
| `soft_text` | `#6F7284` | secondary text |
| `muted` | `#8A8B98` | dim text, dividers, bar track |
| `blue` | `#557C9C` | info, model=Sonnet, plan=max5 |
| `cyan` | `#4F8D91` | chart lines |
| `lavender` | `#77709F` | header, model=Opus, plan=max20 |
| `purple` | `#675D91` | progress-bar fill (uniform across all usage tiers) |
| `pink` | `#A66F87` | plan=pro |
| `rose` | `#AE6677` | errors |
| `green` | `#5F856B` | success |
| `yellow` | `#927B48` | warnings |

Dark-mode variants are the same hues lightened toward white (see the file for exact blend factors) so the palette stays readable if the terminal profile switches with macOS appearance.

One deliberate choice: upstream color-codes the progress-bar *fill* by usage tier (green/yellow/red). This fork keeps the fill a uniform purple and lets the 🟢/🟡/🔴 emoji carry the tier signal instead — because upstream's own tier-threshold selection for the bar fill didn't always agree with the emoji's threshold selection, which looked like a bug (a red-tier-colored bar next to a 🟡 medium icon). Uniform fill sidesteps that mismatch entirely.

### 2. `--no-header` ultra-compact mode

`src/claude_monitor/ui/session_display.py` — the existing `--no-header` flag only hid the title banner upstream; two blank-line inserts and the trailing `⏰ HH:MM:SS 📝 Active session | Ctrl+C to exit` footer were unconditional. This fork gates all of them behind the same flag, so `--no-header` now means what it sounds like: content runs from the first metric line straight through the last, with no leading or trailing padding at all.

### 3. Live-display duplication bug fix

`src/claude_monitor/ui/display_controller.py` — `LiveDisplayManager` created Rich's `Live` with `vertical_overflow="visible"`. When the rendered content height is close to (or equal to) the terminal's row count, printing the last line's newline forces a real terminal scroll, which permanently desyncs `Live`'s internal cursor-position tracking — every refresh after that leaves a stale duplicate frame in the scrollback instead of overwriting in place. This is very noticeable once you size a pane tightly to its content (exactly what `--no-header` invites you to do) and scroll up: dozens of duplicate frames stacked in the scrollback.

Fixed by switching to `vertical_overflow="crop"`, so Rich clips overflow instead of ever scrolling the terminal. Confirmed clean over 60+ refresh cycles at a pane height exactly equal to content height.

### 4. macOS / iTerm2 auto-launch setup (`macos-setup/`)

Not upstream features — a personal automation layer that opens a two-pane iTerm2 window on login:

- **`autolaunch.applescript`** — install into `~/Library/Application Support/iTerm2/Scripts/AutoLaunch/` to auto-run on every iTerm2 launch (skips if already running). Splits one window into two panes and pins their sizes: **top pane, 21 rows × 80 columns** — the live dashboard (`claude-monitor --plan pro --api --no-header`), sized to exactly fit its 21-line compact render (no wrap, no clip, no scroll-desync per the fix above); **bottom pane, 5 rows** — the companion status strip below.
- **`autostart-terminal.sh`** — same layout, runnable by hand instead of via AutoLaunch.
- **`weekly-status.sh`** — the bottom-pane script. Reads the OAuth usage cache that `--api` maintains and prints **5-hour** and **Weekly** rate-limit bars (upstream's dashboard doesn't surface these two windows directly). Polls with `--api-ttl-seconds 60` and a matching `sleep 60`, so data is at most 60s stale — tighter than upstream's 180s default TTL — while still respecting Anthropic's `Retry-After` backoff if the endpoint ever 429s.
- **`combined-monitor.sh`** — a single-pane alternative that prints the full dashboard followed by the same 5-hour/Weekly bars, for anyone who'd rather not split panes.

A non-obvious detail if you adapt this: iTerm2's AppleScript `set rows to N` on a split pane resizes the *whole window*, expanding to fit whichever pane was resized *most recently* while leaving sibling panes at their current pixel size. So the smaller pane must be sized first, and the dashboard pane sized last — reverse the order and the math comes out wrong.

---

## Install

This fork isn't published to PyPI. Install it directly from this repo with [uv](https://docs.astral.sh/uv/):

```bash
uv tool install git+https://github.com/IIISEIII/Angel-core-Claude-Code-Usage-Monitor.git
```

Then, optionally, set up the iTerm2 auto-launch layer:

```bash
mkdir -p ~/.claude-monitor
cp macos-setup/weekly-status.sh ~/.claude-monitor/
chmod +x ~/.claude-monitor/weekly-status.sh

mkdir -p ~/Library/"Application Support"/iTerm2/Scripts/AutoLaunch
cp macos-setup/autolaunch.applescript ~/Library/"Application Support"/iTerm2/Scripts/AutoLaunch/claude-monitor-autolaunch.scpt
```

### Required setup: the iTerm2 "Monitor" profile

The `macos-setup/` scripts assume an iTerm2 profile named exactly **Monitor** exists — create one via iTerm2 → Settings → Profiles → **+**, name it `Monitor`. The theme colors come entirely from `claude-monitor` itself (see above), not the profile, so appearance is up to you. For reference, here's the exact font setting used for the screenshot at the top of this README (Profiles → Text tab):

| Setting | Value |
|---|---|
| Font | JetBrainsMonoNL Nerd Font |
| Style | Medium |
| Size | 8 |
| Horizontal Spacing | 100% |
| Vertical Spacing | 132% |

A Nerd Font isn't strictly required — claude-monitor's icons are standard Unicode emoji and Braille spinner glyphs, not Nerd Font glyphs — any monospace font works. The generous 132% vertical spacing is what gives the dashboard its airy look; a value closer to 100% will pack the same content into a visibly shorter window.

For everything else — installation options, `--plan`, all the other flags, features, troubleshooting — see the original [README.upstream.md](README.upstream.md); none of that changed here.

---

## License

MIT, unchanged from upstream. See [LICENSE](LICENSE). Copyright (c) 2025 Maciej (original author); customizations above (c) 2026 ISEI.
