#!/bin/bash
# Single-pane view: prints claude-monitor's full live dashboard, then
# appends a 5-hour/weekly bar read from the same OAuth usage cache,
# so both live in one tab/one pane without splitting.
CACHE="$HOME/.claude-monitor/api/latest.json"
REFRESH=10

fmt_reset() {
  local epoch=$1
  local now=$(date +%s)
  local diff=$((epoch - now))
  if [ "$diff" -lt 0 ]; then echo "now"; return; fi
  local h=$((diff / 3600))
  local m=$(((diff % 3600) / 60))
  echo "${h}h ${m}m"
}

bar() {
  local pct_int=$1 width=30 filled empty color
  filled=$(( pct_int * width / 100 ))
  (( filled > width )) && filled=$width
  (( filled < 0 )) && filled=0
  empty=$(( width - filled ))
  if   (( pct_int < 50 )); then color="\033[32m"
  elif (( pct_int < 80 )); then color="\033[33m"
  else color="\033[31m"; fi
  printf "${color}["
  (( filled > 0 )) && printf '█%.0s' $(seq 1 "$filled")
  printf "\033[38;5;238m"
  (( empty > 0 )) && printf '░%.0s' $(seq 1 "$empty")
  printf "\033[0m]"
}

while true; do
  clear
  claude-monitor --plan pro --api --once --no-clear

  if [ -f "$CACHE" ]; then
    limits_line=$(python3 -c "
import json
d = json.load(open('$CACHE'))['limits']
print(d['five_hour']['used_percentage'], d['five_hour']['resets_at_epoch'], d['seven_day']['used_percentage'], d['seven_day']['resets_at_epoch'])
" 2>/dev/null)
    read -r five five_reset week week_reset <<<"$limits_line"

    echo
    printf "  5-hour : %s %5s%%  (resets in %s)\n" "$(bar "${five%.*}")" "$five" "$(fmt_reset "$five_reset")"
    printf "  Weekly : %s %5s%%  (resets in %s)\n" "$(bar "${week%.*}")" "$week" "$(fmt_reset "$week_reset")"
  fi

  sleep "$REFRESH"
done
