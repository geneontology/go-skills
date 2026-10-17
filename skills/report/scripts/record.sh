#!/usr/bin/env bash
# record.sh — write one curator report as a JSON file under ~/.go-jupyter/reports/.
#
# Usage: record.sh --category <error|wrong-tool|idea|complaint|praise|other>
#                  --note "<the curator's words>" [--context "<one line from the agent>"]
#                  [--issue-url <url>]
# Prints the path of the file written. Exit 2 on a bad category or a missing note.
#
# The record carries what the operators need to find the moment later: the
# session id and the last assistant turn's id, taken from the newest transcript
# under ~/.claude/projects/ for the current directory, and the skill that turn
# was attributed to. Nothing here needs a token, and nothing is sent anywhere:
# the hub's trace sync picks the file up and attaches it to the session's trace.
set -euo pipefail

category=""; note=""; context=""; issue_url=""
while [ $# -gt 0 ]; do
    case "$1" in
        --category)  category="${2:-}"; shift ;;
        --note)      note="${2:-}"; shift ;;
        --context)   context="${2:-}"; shift ;;
        --issue-url) issue_url="${2:-}"; shift ;;
        *) echo "record.sh: unknown argument: $1" >&2; exit 2 ;;
    esac
    shift
done
case "$category" in
    error|wrong-tool|idea|complaint|praise|other) ;;
    *) echo "record.sh: --category must be one of error, wrong-tool, idea, complaint, praise, other" >&2; exit 2 ;;
esac
[ -n "$note" ] || { echo "record.sh: --note is required (the curator's own words)" >&2; exit 2; }

# The transcript Claude Code is writing for this session: the newest .jsonl in
# the project directory for the current working directory (its name is the cwd
# with every "/" turned into "-"), falling back to the newest anywhere.
slug="$(pwd | tr '/' '-')"
transcript="$(ls -t "$HOME/.claude/projects/$slug"/*.jsonl 2>/dev/null | head -n 1 || true)"
[ -n "$transcript" ] || transcript="$(ls -t "$HOME"/.claude/projects/*/*.jsonl 2>/dev/null | head -n 1 || true)"

session_id=""; turn_uuid=""; skill=""
if [ -n "$transcript" ]; then
    session_id="$(basename "$transcript" .jsonl)"
    # Last assistant entry: its uuid and the skill it was attributed to, if any.
    read -r turn_uuid skill < <(
        tac "$transcript" | python3 -c '
import json, sys
for line in sys.stdin:
    try:
        d = json.loads(line)
    except ValueError:
        continue
    if d.get("type") == "assistant":
        print(d.get("uuid") or "-", d.get("attributionSkill") or "-")
        break
else:
    print("- -")
' 2>/dev/null || echo "- -"
    )
    [ "$turn_uuid" = "-" ] && turn_uuid=""
    [ "$skill" = "-" ] && skill=""
fi

out_dir="$HOME/.go-jupyter/reports"
mkdir -p "$out_dir"
chmod 700 "$out_dir"
ts="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
short="${session_id:0:8}"
[ -n "$short" ] || short="nosession"
path="$out_dir/$(date -u +%Y%m%dT%H%M%SZ)-$short.json"

python3 - "$path" "$ts" "$category" "$note" "$context" "$issue_url" "$session_id" "$turn_uuid" "$skill" "$transcript" <<'EOF'
import json, os, socket, sys
path, ts, category, note, context, issue_url, session_id, turn_uuid, skill, transcript = sys.argv[1:]
record = {
    "version": 1,
    "timestamp": ts,
    "user": os.environ.get("USER") or os.environ.get("LOGNAME") or "",
    "host": socket.gethostname(),
    "cwd": os.getcwd(),
    "session_id": session_id or None,
    "transcript": transcript or None,
    "turn_uuid": turn_uuid or None,
    "skill": skill or None,
    "category": category,
    "note": note,
    "context": context or None,
    "issue_url": issue_url or None,
}
with open(path, "w") as fh:
    json.dump(record, fh, indent=2, ensure_ascii=False)
    fh.write("\n")
os.chmod(path, 0o600)
print(path)
EOF
