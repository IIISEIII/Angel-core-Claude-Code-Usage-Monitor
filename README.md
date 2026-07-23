# ISEI's Angel Core Claude Usage Monitor Customize

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![日本語](https://img.shields.io/badge/日本語-README-blue.svg)](README.ja.md)

A personal fork of [**Maciek-roboblog/Claude-Code-Usage-Monitor**](https://github.com/Maciek-roboblog/Claude-Code-Usage-Monitor) — all credit for the tool itself goes to **Maciek**. This fork doesn't add anything; it just repaints the dashboard in a softer, more pastel mood ("Angelcore") and fixes one real bug found along the way. If you want the actively maintained original, [go use that one](https://github.com/Maciek-roboblog/Claude-Code-Usage-Monitor) — this repo is just a record of one particular desk setup, kept public in case the theme or the iTerm2 automation is useful to someone else too. Original README preserved at [README.upstream.md](README.upstream.md); the MIT license is untouched.

![Dashboard](doc/angelcore-dashboard.png)

---

## Prerequisites

- macOS + [iTerm2](https://iterm2.com) — the auto-launch scripts are iTerm2-specific (`claude-monitor` itself runs anywhere)
- [uv](https://docs.astral.sh/uv/), for installing
- An iTerm2 profile named exactly **Monitor**: iTerm2 → Settings → Profiles → **+**. Appearance is up to you — colors come from `claude-monitor` itself, not the profile — but here's the font from the screenshot above, for reference (Profiles → Text tab):

  | Setting | Value |
  |---|---|
  | Font | JetBrainsMonoNL Nerd Font |
  | Style | Medium |
  | Size | 8 |
  | Horizontal Spacing | 100% |
  | Vertical Spacing | 132% |

  Nerd Font is a nice-to-have, not a requirement — the icons are plain Unicode emoji, so any monospace font works. The generous 132% vertical spacing is what gives the dashboard its room-to-breathe look; closer to 100% packs the same content into a shorter window.
- `~/.local/bin` on your `PATH` — that's where `uv tool install` puts the `claude-monitor` binary, and the setup scripts call it by name. `uv` will tell you if it isn't set up yet.

---

## Install

```bash
uv tool install git+https://github.com/IIISEIII/Angel-core-Claude-Code-Usage-Monitor.git
```

Then, optionally, the iTerm2 auto-launch layer:

```bash
mkdir -p ~/.claude-monitor
cp macos-setup/weekly-status.sh ~/.claude-monitor/
chmod +x ~/.claude-monitor/weekly-status.sh

mkdir -p ~/Library/"Application Support"/iTerm2/Scripts/AutoLaunch
cp macos-setup/autolaunch.applescript ~/Library/"Application Support"/iTerm2/Scripts/AutoLaunch/claude-monitor-autolaunch.scpt
```

Next time iTerm2 opens, a two-pane window shows up on its own — no more chasing it down manually. For everything else — install options, `--plan`, the rest of the flags, the full feature list — see [README.upstream.md](README.upstream.md); none of that changed here.

---

## What changed from upstream

Three source files edited, four scripts added under [`macos-setup/`](macos-setup/).

### The colors

`themes.py` — both theme tables rewritten from upstream's xterm-256 palette to something quieter:

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

Dark mode gets the same hues, lightened. Progress bars are now a uniform purple rather than color-coded by usage tier — upstream's tier logic for the *bar* didn't always agree with the tier logic for the *emoji* beside it, so you'd occasionally get a red-tier bar next to a calm yellow 🟡. The emoji alone carries that signal now; the bar just fills up.

### `--no-header`, for real this time

`session_display.py` — upstream's `--no-header` hid the title banner but still printed two blank lines and a trailing "Active session" footer unconditionally. Both are now gated on the same flag, so `--no-header` finally means what it says: first line to last, nothing extra on either end.

### The scrollback ghost

`display_controller.py` — this one's a genuine bug, not a preference. Rich's `Live` was created with `vertical_overflow="visible"`. Size a pane exactly to its content — which `--no-header` all but invites you to do — and every refresh nudges the terminal into scrolling once, permanently desyncing `Live`'s cursor tracking. Scroll up afterward and you'll find dozens of ghost frames stacked in the scrollback, one per refresh, forever. Switched to `vertical_overflow="crop"`, which clips instead of scrolling. Confirmed clean over 60+ refreshes at a pane sized exactly to its content.

### The iTerm2 layer

`macos-setup/` — not upstream, just automation. `autolaunch.applescript` opens a two-pane iTerm2 window on startup, sized to fit the compact render exactly (21 rows for the dashboard, 5 for the status strip below). `weekly-status.sh` reads the same `--api` usage cache and prints **5-hour** / **Weekly** bars that upstream's dashboard doesn't surface directly, polling every 60s instead of the 180s default. `combined-monitor.sh` is a one-pane version for anyone who'd rather skip the split.

One iTerm2 quirk worth knowing if you adapt this: resizing a pane's `rows` resizes the *whole window*, growing to fit whichever pane you touched last while its sibling holds still. Resize the small pane first and the dashboard pane last — backwards, and the math won't come out right.

---

## License

MIT, same as upstream. See [LICENSE](LICENSE). Copyright (c) 2025 Maciej (original author); the changes above, (c) 2026 ISEI.
