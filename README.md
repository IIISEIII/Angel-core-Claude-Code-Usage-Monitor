# ISEI's Angel Core Claude Usage Monitor Customize

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![日本語](https://img.shields.io/badge/日本語-README-blue.svg)](README.ja.md)

A personal fork of [**Maciek-roboblog/Claude-Code-Usage-Monitor**](https://github.com/Maciek-roboblog/Claude-Code-Usage-Monitor) — every credit for the tool itself belongs to **Maciek**. This fork adds no new functionality; it simply attends to the dashboard's appearance, dressing it in a softer, more pastel mood ("Angelcore"), and quietly resolves one genuine rendering bug encountered along the way. If the actively maintained original is what you're after, it's waiting for you [here](https://github.com/Maciek-roboblog/Claude-Code-Usage-Monitor). This repository exists to keep a record of one particular setup, made public in case it's of use to someone doing similar work. The original README is preserved at [README.upstream.md](README.upstream.md), and the MIT license is unchanged.

![Dashboard](doc/angelcore-dashboard.png)

---

## Prerequisites

- macOS with [iTerm2](https://iterm2.com) — the auto-launch scripts are iTerm2-specific; `claude-monitor` itself is happy to run anywhere.
- [uv](https://docs.astral.sh/uv/), for installing.
- An iTerm2 profile named exactly **Monitor**: iTerm2 → Settings → Profiles → **+**. Its appearance is entirely up to you — the colors come from `claude-monitor` itself, not the profile — but for reference, here is the font used in the screenshot above (Profiles → Text tab):

  | Setting | Value |
  |---|---|
  | Font | JetBrainsMonoNL Nerd Font |
  | Style | Medium |
  | Size | 8 |
  | Horizontal Spacing | 100% |
  | Vertical Spacing | 132% |

  A Nerd Font is a pleasant extra, not a requirement — the icons are ordinary Unicode emoji, so any monospace font will serve. The generous 132% vertical spacing is what gives the dashboard its unhurried, airy look; closer to 100% will fit the same content into a shorter window, should you prefer that.
- `~/.local/bin` on your `PATH` — that's where `uv tool install` places the `claude-monitor` binary, and the setup scripts call it by name rather than by full path. `uv` will let you know if this needs attending to.

---

## Install

```bash
uv tool install git+https://github.com/IIISEIII/Angel-core-Claude-Code-Usage-Monitor.git
```

Then, should you like the full experience, the iTerm2 auto-launch layer:

```bash
mkdir -p ~/.claude-monitor
cp macos-setup/weekly-status.sh ~/.claude-monitor/
chmod +x ~/.claude-monitor/weekly-status.sh

mkdir -p ~/Library/"Application Support"/iTerm2/Scripts/AutoLaunch
cp macos-setup/autolaunch.applescript ~/Library/"Application Support"/iTerm2/Scripts/AutoLaunch/claude-monitor-autolaunch.scpt
```

From then on, a two-pane window will be waiting for you each time iTerm2 opens — no further attention required. For everything else — installation options, `--plan`, the remaining flags, the full feature list — please see [README.upstream.md](README.upstream.md); none of that has changed here.

---

## What changed from upstream

Three source files were edited, and four scripts were added under [`macos-setup/`](macos-setup/).

### The colors

`themes.py` — both theme tables were rewritten, from upstream's xterm-256 palette to something quieter:

| Role | Hex | Used for |
|---|---|---|
| `foreground` | `#3F3E4A` | primary text |
| `soft_text` | `#6F7284` | secondary text |
| `muted` | `#8A8B98` | dim text, dividers, bar track |
| `blue` | `#557C9C` | info, model=Sonnet, plan=max5 |
| `cyan` | `#4F8D91` | chart lines |
| `lavender` | `#77709F` | header, model=Opus, plan=max20 |
| `purple` | `#675D91` | progress-bar fill |
| `pink` | `#A66F87` | plan=pro |
| `rose` | `#AE6677` | errors |
| `green` | `#5F856B` | success |
| `yellow` | `#927B48` | warnings |

Dark mode receives the same hues, lightened. The progress bars now fill in a uniform purple rather than being color-coded by usage tier — upstream's tier judgment for the *bar* did not always agree with its judgment for the *emoji* beside it, occasionally producing a red-toned bar next to a perfectly calm yellow 🟡. That small disagreement has been retired; the emoji alone now carries the signal, and the bar simply fills, without opinion.

### `--no-header`, true to its word

`session_display.py` — upstream's `--no-header` hid the title banner, but two blank lines and a trailing "Active session" footer were still printed unconditionally. Both are now governed by the same flag, so `--no-header` at last means precisely what it says: the first line to the last, with nothing extra appended at either end.

### A small matter in the scrollback

`display_controller.py` — this one was a genuine defect, not a matter of taste. Rich's `Live` had been created with `vertical_overflow="visible"`. When a pane is sized precisely to its content — which `--no-header` rather invites one to do — each refresh nudges the terminal into a single scroll, which permanently unsettles `Live`'s sense of where its own cursor sits. Scroll upward afterward, and a quiet procession of stale frames will be found waiting in the scrollback, one per refresh, indefinitely. The remedy was to switch to `vertical_overflow="crop"`, so that overflow is trimmed rather than the terminal ever being asked to scroll. Verified clean across more than sixty refreshes, with the pane sized exactly to its content.

### The iTerm2 layer

`macos-setup/` — not an upstream feature, simply some automation in service of convenience. `autolaunch.applescript` opens a two-pane iTerm2 window on startup, each pane sized to fit its render exactly (21 rows for the dashboard, 5 for the status strip beneath it). `weekly-status.sh` reads the same `--api` usage cache and displays the **5-hour** and **Weekly** bars that upstream's dashboard doesn't surface directly, checking in every 60 seconds rather than the default 180. `combined-monitor.sh` offers the same pair of bars in a single pane, for anyone who'd rather not split the window.

One point worth noting, should this setup be adapted elsewhere: resizing a pane's `rows` in iTerm2 resizes the *entire window*, which grows to accommodate whichever pane was most recently attended to, while its neighbor is left exactly as it was. The smaller pane should therefore be sized first, and the dashboard pane last — done in the other order, the arithmetic will not oblige.

---

## License

MIT, unchanged from upstream. See [LICENSE](LICENSE). Copyright (c) 2025 Maciej (original author); the changes above, (c) 2026 ISEI.
