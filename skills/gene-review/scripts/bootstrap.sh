#!/usr/bin/env bash
# bootstrap.sh — make sure a working ai-gene-review checkout exists and is set up.
#
# Idempotent. Safe to run at the start of every gene-review task. Needs: git,
# curl or uv, network. Needs NO GitHub credentials (public repo, HTTPS, no push).
#
# Env knobs (all optional):
#   AIGR_HOME        where the checkout lives           (default: ~/ai-gene-review)
#   AIGR_ORGANISMS   space-separated organism dirs to    (default: none — genes/ is
#                    check out under genes/, e.g. "DANRE   populated by fetch-gene)
#                    human"; ignored for a full clone
#   AIGR_FULL=1      full working tree instead of sparse (~4 GB vs ~250 MB)
#   AIGR_NO_UPDATE=1 do not `git pull` an existing checkout
#   UV_PROJECT_ENVIRONMENT  pre-built shared venv; honoured by uv automatically
#
# Prints a short status block on stdout; exits non-zero only on a hard failure.
set -euo pipefail

REPO_URL="https://github.com/ai4curation/ai-gene-review"
AIGR_HOME="${AIGR_HOME:-$HOME/ai-gene-review}"
# Directories the tooling reads outside genes/<ORG>/. `conf` is not optional:
# without it the reference validator silently mis-resolves file: references
# and GO_REF citations.
CORE_DIRS="src scripts conf cache .claude docs interpro gocams"

say()  { printf '  %s\n' "$*"; }
fail() { printf 'bootstrap: %s\n' "$*" >&2; exit 1; }

command -v git >/dev/null || fail "git is not installed"

# ---- 1. checkout -----------------------------------------------------------
if [ ! -e "$AIGR_HOME/justfile" ]; then
  say "cloning ai-gene-review into $AIGR_HOME (first time only)"
  if [ "${AIGR_FULL:-0}" = "1" ]; then
    git clone --depth 1 --no-single-branch "$REPO_URL" "$AIGR_HOME"
  else
    git clone --depth 1 --no-single-branch --filter=blob:none --sparse \
      "$REPO_URL" "$AIGR_HOME"
    # shellcheck disable=SC2086
    git -C "$AIGR_HOME" sparse-checkout set $CORE_DIRS
  fi
elif [ -d "$AIGR_HOME/.git" ] && [ "${AIGR_NO_UPDATE:-0}" != "1" ]; then
  say "updating existing checkout"
  git -C "$AIGR_HOME" pull -q --ff-only 2>/dev/null \
    || say "note: could not fast-forward (local changes?); continuing with what is there"
fi

# ---- 2. organism directories (sparse checkouts only) -----------------------
if [ -d "$AIGR_HOME/.git" ] && git -C "$AIGR_HOME" sparse-checkout list >/dev/null 2>&1; then
  for org in ${AIGR_ORGANISMS:-}; do
    # A directory can exist with only a single reference gene checked out.
    # Adding the whole cone is idempotent and also includes review history.
    say "adding genes/$org to the sparse checkout"
    git -C "$AIGR_HOME" sparse-checkout add "genes/$org" "history/genes/$org" \
      || fail "could not hydrate genes/$org; do not fetch genes until this is resolved"
  done
fi

# ---- 3. tooling ------------------------------------------------------------
export PATH="$HOME/.local/bin:$PATH"
if ! command -v uv >/dev/null; then
  say "installing uv"
  curl -LsSf https://astral.sh/uv/install.sh | sh -s -- -q
fi
if ! command -v just >/dev/null; then
  say "installing just"
  uv tool install -q rust-just
fi
say "syncing Python environment (slow the first time)"
( cd "$AIGR_HOME" && uv sync -q --group dev --frozen )

# ---- 4. status -------------------------------------------------------------
echo
echo "ai-gene-review is ready"
say "AIGR_HOME:   $AIGR_HOME"
say "checkout:    $( [ -d "$AIGR_HOME/.git" ] && { git -C "$AIGR_HOME" sparse-checkout list >/dev/null 2>&1 && echo sparse || echo full; } || echo 'plain directory (no .git)')"
say "revision:    $(git -C "$AIGR_HOME" log -1 --format='%h %ad' --date=short 2>/dev/null || echo unknown)"
if sparse_dirs=$(git -C "$AIGR_HOME" sparse-checkout list 2>/dev/null); then
  # Only whole organism cones count; genes/human/SHH does not mean all of human.
  organisms=$(printf '%s\n' "$sparse_dirs" | awk -F/ '
    $0 == "genes" { printf "(all organisms) " }
    $1 == "genes" && NF == 2 { printf "%s ", $2 }
  ')
else
  organisms=$(for dir in "$AIGR_HOME"/genes/*; do
    [ ! -d "$dir" ] || printf '%s ' "${dir##*/}"
  done)
fi
say "organisms:   ${organisms:-none}"
say "venv:        ${UV_PROJECT_ENVIRONMENT:-$AIGR_HOME/.venv}"
say "just:        $(command -v just)"
missing=""
for v in EDISON_API_KEY ASTA_API_KEY PERPLEXITY_API_KEY; do [ -n "${!v:-}" ] || missing="$missing $v"; done
[ -z "$missing" ] || say "deep research: unavailable (unset:$missing) — synthesise literature manually"
