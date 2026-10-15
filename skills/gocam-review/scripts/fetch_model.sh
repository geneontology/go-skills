#!/usr/bin/env bash
# fetch_model.sh — download a GO-CAM model, read-only, from Noctua's public
# download route. No token, no cookie, nothing is written to Noctua.
#
# usage: fetch_model.sh <model id | Noctua URL> [production|dev] [outdir] [--dry-run]
#   model id   gomodel:ZFIN_ZDB-GENE-991207-22, ZFIN_ZDB-GENE-991207-22,
#              gomodel:68d3f4b800000234, or a Noctua URL that contains the id
#              (…/editor/graph/gomodel:X, …?model_id=gomodel:X, …/download/gomodel:X/owl)
#   production (default) http://noctua.geneontology.org
#   dev                  http://noctua-dev.berkeleybop.org
#   outdir     default: $PWD
#
# Writes <outdir>/<id>.ttl (the route is called /owl but the body is Turtle)
# and <outdir>/<id>.gpad, and prints both paths. Exit 1 if the model is not
# found or the body is not a model.
set -euo pipefail
dry=0; args=()
for a in "$@"; do case "$a" in --dry-run) dry=1 ;; *) args+=("$a") ;; esac; done
set -- "${args[@]}"
arg="${1:-}"; env="${2:-production}"; out="${3:-$PWD}"
[ -n "$arg" ] || { sed -n '2,17p' "$0" >&2; exit 2; }
case "$env" in
    production|prod) host="http://noctua.geneontology.org" ;;
    dev)             host="http://noctua-dev.berkeleybop.org" ;;
    *) echo "environment must be production or dev, not '$env'" >&2; exit 2 ;;
esac
# Pull the id out of whatever was given.
id="$arg"
case "$id" in
    *model_id=*)   id="${id#*model_id=}"; id="${id%%&*}" ;;
    */download/*)  id="${id#*/download/}"; id="${id%%/*}" ;;
    */graph/*)     id="${id#*/graph/}"; id="${id%%[/?#]*}" ;;
esac
id="${id#gomodel:}"
case "$id" in
    *[!A-Za-z0-9_:.-]*|'') echo "that does not look like a model id: '$arg'" >&2; exit 2 ;;
esac
if [ "$dry" -eq 1 ]; then echo "would fetch gomodel:$id from $host into $out"; exit 0; fi
mkdir -p "$out"
ttl="$out/$id.ttl"; gpad="$out/$id.gpad"
if ! curl -fsS --retry 3 --retry-delay 2 -o "$ttl" "$host/download/gomodel:$id/owl"; then
    echo "no model gomodel:$id on $host (the route answers 400 for an unknown id)" >&2; exit 1
fi
if ! head -c 200 "$ttl" | grep -q '@prefix'; then
    echo "the download for gomodel:$id is not a model (first bytes: $(head -c 80 "$ttl" | tr '\n' ' '))" >&2
    rm -f "$ttl"; exit 1
fi
curl -fsS --retry 2 -o "$gpad" "$host/download/gomodel:$id/gpad" 2>/dev/null || { echo "note: no GPAD export for gomodel:$id (continuing with the Turtle only)" >&2; rm -f "$gpad"; }
echo "model:  gomodel:$id ($env, $host)"
echo "ttl:    $ttl"
[ -f "$gpad" ] && echo "gpad:   $gpad"
