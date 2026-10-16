---
name: report
description: Record what a curator wants the operators of the GO AI Hub to hear, in their own words, and tie it to the moment it refers to. Use when the user invokes /report, or whenever they say something went wrong, that a tool or skill was the wrong one or did a poor job, that they have an idea or a wish, a complaint, or praise, about the hub, the agent, a skill or the documentation. Listen first; one optional question; then write the record and, only when there is something to fix, offer to open an issue.
license: BSD-3-Clause
argument-hint: "[what happened, or what's on your mind]"
metadata:
  version: "0.1.0"
  source: https://github.com/geneontology/go-skills/tree/main/skills/report
  maintainer: geneontology
---

# Report: tell the operators something

This is the curator's channel to the people who run the hub and maintain the
skills. It is not a bug form. A curator may vent, praise, ask for something,
or point at a moment that went wrong, and the record keeps their words and the
place in the session they refer to, so the operators can find that moment later
in the session traces and act on it.

## How to behave

1. **Listen.** If the user gave the report with the command (`/report the model
   it picked was wrong`), that is the note. Otherwise ask one open question and
   stop: *"What happened, or what's on your mind? A sentence is enough."*
2. **Keep their words.** The note is what the user said, verbatim or lightly
   tidied; never your paraphrase of what you think they meant. If you can add
   one line of context (what you were doing at the time, which skill was in
   play, a model or paper id), put it in the context field, clearly yours.
3. **One question at most, and only if it changes what gets recorded**: for
   example which model or gene they mean when two were in play. If the user
   says "skip", "never mind" or "just record it", record what you have and
   move on. Never turn this into an interview.
4. **Pick the category** yourself, from what they said; do not ask them to
   choose: `error` (the agent or a tool did something wrong), `wrong-tool`
   (the wrong skill or tool was used, or one was missing), `idea` (a
   suggestion or a wish), `complaint` (something is bad or annoying, with no
   specific fix asked for), `praise`, or `other`.
5. **Write the record** with the script (it finds the session and the last
   turn itself; nothing is sent anywhere):

   ```sh
   "${CLAUDE_SKILL_DIR}/scripts/record.sh" --category <category> \
     --note "<the user's words>" --context "<your one line, optional>"
   ```

   It prints the path of the file under `~/.go-jupyter/reports/`. Tell the
   user, in one line, that it is recorded and that the operators will see it
   together with this point in the session. Do not read the file back to them.
6. **Offer an issue only when there is something to fix**: an `error`, a
   `wrong-tool`, or an `idea` about a skill or the documentation. Say what you
   would file and where, and wait for a yes. For a `complaint`, `praise` or
   `other`, do not offer; the record is the point.
7. **If they say yes**, file it with `gh` under their own GitHub login (the hub
   signs `gh` in at login; if `gh auth status` fails, say so and stop, the
   record stands on its own):

   ```sh
   gh issue create --repo geneontology/go-skills --label skill-correction \
     --title "<skill>: <one line>" --body-file <file>
   ```

   Use the label `skill-correction` for an error or wrong-tool report about a
   skill, `documentation` for a documentation problem, `new-skill` for an idea
   that needs a skill that does not exist. The body follows the repository's
   issue form, as headings: **Skill** (directory name, or "none"), **What
   happened** (the note), **What you expected**, **Input involved** (ids,
   paper, prompt; optional), **Where** (`GO AI Hub`), **Session or trace
   reference** (the session id from the record), and a last line: *Filed from
   a GO AI Hub session by the curator's agent, at the curator's request.*
   Then add the issue URL to the record:

   ```sh
   "${CLAUDE_SKILL_DIR}/scripts/record.sh" --category <category> \
     --note "<the same note>" --issue-url <url>
   ```

   (This writes a second record with the URL; the operators treat the pair as
   one.) Tell the user the URL.
8. **Then go back to what you were doing.** A report is never a reason to
   redo, undo or re-explain the work it is about unless the user asks.

## What the record holds

A JSON file, one per report, mode 0600, under `~/.go-jupyter/reports/`:
timestamp (UTC), user, host, working directory, session id, the last
assistant turn's id and the skill it was attributed to, category, the note,
your context line, and the issue URL if one was filed. The hub's trace sync
reads these files and marks the matching turn in the session trace, so a
report is searchable by category and by the curator's words. The file is the
curator's; they may read or delete it.

## Things not to do

- Do not ask for consent, severity ratings, reproduction steps, or anything a
  bug tracker would. If the user wants to give more, they will.
- Do not file an issue without a yes, and never on a repository other than
  go-skills unless the user names it.
- Do not soften, summarise or correct the user's words in the note. Context
  is where your view goes, marked as yours.
- Do not treat a report as an instruction to change a skill on the box: skills
  are read-only links here, and the change goes through the issue.
