-- Opens the claude-monitor dashboard (in the "Monitor" iTerm profile) whenever
-- iTerm2 starts, unless it's already running. Splits into two panes: the
-- live dashboard on top, the weekly-status companion script below.
--
-- Install: copy this file to
--   ~/Library/Application Support/iTerm2/Scripts/AutoLaunch/
-- (create the AutoLaunch folder if it doesn't exist), and copy
-- weekly-status.sh from this same directory to ~/.claude-monitor/.
-- Requires an iTerm2 profile named "Monitor" and claude-monitor
-- installed with the Angelcore patches from this fork (see ../README.md).
--
-- Pane sizes are pinned (80 columns, 21 rows for the dashboard, 5 rows
-- for the status strip) so the claude-monitor render always fits without
-- wrapping (its progress bars need >=80 cols). --no-header (plus the
-- matching edits in claude_monitor/ui/session_display.py) drops the
-- title banner, all leading/trailing blank padding, and the trailing
-- "Active session" footer, so content runs exactly from "Cost Usage" to
-- "Limit resets at" (21 lines) -- and the dashboard pane is exactly that
-- height. This only works because of a second edit in
-- claude_monitor/ui/display_controller.py: LiveDisplayManager's Rich
-- Live was created with vertical_overflow="visible", which lets Rich
-- scroll the real terminal on overflow and permanently desyncs its
-- cursor-position tracking -- every refresh after that leaves a stale
-- duplicate frame in the scrollback (confirmed at both rows=21 and
-- rows=22). Changed to vertical_overflow="crop" so Rich clips overflow
-- instead of ever scrolling the terminal, which is what makes a flush,
-- no-margin fit safe. iTerm2 resizes the *whole window* to fit whichever
-- pane's rows are set last, so the smaller pane must be sized first and
-- the dashboard pane sized last.

set homeDir to (system attribute "HOME")
set weeklyScript to homeDir & "/.claude-monitor/weekly-status.sh"

set alreadyRunning to false
try
	do shell script "pgrep -f " & quoted form of weeklyScript
	set alreadyRunning to true
end try

if not alreadyRunning then
	tell application "iTerm"
		activate
		set newWindow to (create window with profile "Monitor")
		set topSession to current session of newWindow
		tell topSession
			set statusSession to (split horizontally with profile "Monitor")
		end tell
		tell statusSession
			set rows to 5
			write text weeklyScript
		end tell
		tell topSession
			set rows to 21
			set columns to 80
			write text "claude-monitor --plan pro --api --no-header"
		end tell
	end tell
end if
