---
name: summary
description: Show the curator what this session actually did, from the session transcript rather than from memory. Use when the user invokes /summary, asks "what did you do", "what did we change", "which models did you touch", "what did you save and where", or wants a record of the session for themselves or a reviewer. Runs the hub's summary tool and presents its output as is.
license: BSD-3-Clause
argument-hint: "[optional: a session id]"
metadata:
  version: "0.1.0"
  source: https://github.com/geneontology/go-skills/tree/main/skills/summary
  maintainer: geneontology
---

# Summary: what this session did

The GO AI Hub keeps a summary tool, `go-jupyter-session-summary`, that reads
the session's transcript and lists what happened: GO-CAM model writes (model
id, operation, server), drop-box and other GitHub writes, commits and pushes,
files written, `/report` records, and then the lookups. It is written from the
tool calls and their results, not from what the agent says about itself, so
it is the record the curator and a reviewer can both trust. The same summary
is written automatically when a session ends.

## How to behave

1. **Run the tool, do not reconstruct the session yourself.** For the current
   session:

   ```sh
   go-jupyter-session-summary --write
   ```

   With an argument that looks like a session id, pass `--session <id>`. The
   tool prints the summary and saves it under `~/.go-jupyter/summaries/<session
   id>.md` (and `.json`).
2. **Show the "Changes made" section verbatim**, every line, including the
   ones marked **FAILED**. Then the rest of the summary, shortened only where
   the user asked for brevity. Do not drop, reorder or reword entries, and do
   not add changes the tool did not list; if you believe something is missing
   or mislabelled, say so in one sentence after the summary (the tool reads
   commands, so a write hidden in a script or a variable shows up as "payload
   built elsewhere").
3. **Name the saved file** so the user can keep or send it, and mention that
   the hub archives the transcript it was made from.
4. If the command is not found, say the summary tool is not installed on this
   host and stop; do not write a summary from memory in its place. If the
   tool reports no transcript, say so.

A model write at PRODUCTION in the summary is not expected on this hub (the
hub only writes to noctua-dev); point it out to the user if it appears.
