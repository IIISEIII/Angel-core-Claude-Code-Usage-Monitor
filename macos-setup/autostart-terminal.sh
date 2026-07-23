#!/bin/bash
# Opens one iTerm2 tab, split into two panes: the live claude-monitor
# dashboard on top (smooth internal refresh) and the weekly-status
# companion script in a smaller pane below (60s refresh). Both panes use
# the "Monitor" profile so fonts match. Run this manually, or point
# iTerm2's Scripts > AutoLaunch at autolaunch.applescript to run it on
# every iTerm2 launch.
#
# Requires: claude-monitor installed with the Angelcore patches from
# this fork (see ../README.md), and an iTerm2 profile named "Monitor".
#
# Pane sizes are pinned (80 columns, 21 rows for the dashboard, 5 rows
# for the status strip) so the claude-monitor render always fits without
# wrapping (its progress bars need >=80 cols). --no-header (plus the
# matching edits in claude_monitor/ui/session_display.py) drops the
# title banner, all leading/trailing blank padding, and the trailing
# "Active session" footer, so content runs exactly from "Cost Usage" to
# "Limit resets at" (21 lines) -- and the dashboard pane is exactly that
# height. This only works because of a second edit in
# claude_monitor/ui/display_controller.py: LiveDisplayManager's Rich
# Live was created with vertical_overflow="visible", which lets Rich
# scroll the real terminal on overflow and permanently desyncs its
# cursor-position tracking -- every refresh after that leaves a stale
# duplicate frame in the scrollback (confirmed at both rows=21 and
# rows=22). Changed to vertical_overflow="crop" so Rich clips overflow
# instead of ever scrolling the terminal, which is what makes a flush,
# no-margin fit safe. iTerm2 resizes the *whole window* to fit whichever
# pane's rows are set last, so the smaller pane must be sized first and
# the dashboard pane sized last.

osascript <<EOF
tell application "iTerm"
  activate
  set newWindow to (create window with profile "Monitor")
  set topSession to current session of newWindow
  tell topSession
    set statusSession to (split horizontally with profile "Monitor")
  end tell
  tell statusSession
    set rows to 5
    write text "$HOME/.claude-monitor/weekly-status.sh"
  end tell
  tell topSession
    set rows to 21
    set columns to 80
    write text "claude-monitor --plan pro --api --no-header"
  end tell
end tell
EOF
