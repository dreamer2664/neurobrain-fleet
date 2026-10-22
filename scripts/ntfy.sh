#!/usr/bin/env bash
# ntfy bus helper. The fleet coordinates here: 8 agents, one topic.
#   ./scripts/ntfy.sh pub "message"
#   ./scripts/ntfy.sh read [n]
#   ./scripts/ntfy.sh watch          # follow live
set -uo pipefail
TOPIC=${TOPIC:-neuralbrain}
NTFY=${NTFY:-https://ntfy.sh}
cmd=${1:-read}

case "$cmd" in
  pub)
    shift
    msg="${*:-ping}"
    curl -s -o /dev/null -w "sent %{http_code}\n" \
      -H "Title: neurobrain" -H "Tags: robot" -d "$msg" "$NTFY/$TOPIC"
    ;;
  read)
    n=${2:-50}
    curl -s "$NTFY/$TOPIC/json?poll=1&since=all" | tail -n "$n" | \
      python3 -c '
import sys, json
for line in sys.stdin:
    try: d = json.loads(line)
    except Exception: continue
    if d.get("event") != "message": continue
    import time
    ts = time.strftime("%H:%M", time.gmtime(d.get("time", 0)))
    print(f"{ts}  {d.get(\"message\",\"\")}")
'
    ;;
  watch)
    curl -s "$NTFY/$TOPIC/json" | python3 -c '
import sys, json
for line in sys.stdin:
    try: d = json.loads(line)
    except Exception: continue
    if d.get("event") == "message":
        print(d.get("message", ""), flush=True)
'
    ;;
  *)
    echo "usage: ntfy.sh pub <msg> | read [n] | watch"; exit 2 ;;
esac
