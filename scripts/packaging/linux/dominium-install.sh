#!/usr/bin/env sh
set -eu

usage() {
  echo "Usage: $(basename "$0") [--artifact-root DIR] [--scope portable|user|system] [--dry-run] [--deterministic 0|1]"
}

ARTIFACT_ROOT=""
SCOPE="portable"
DRY_RUN="0"
DETERMINISTIC="1"

while [ $# -gt 0 ]; do
  case "$1" in
    --artifact-root) ARTIFACT_ROOT="${2:-}"; shift 2;;
    --scope) SCOPE="${2:-}"; shift 2;;
    --dry-run) DRY_RUN="1"; shift 1;;
    --deterministic) DETERMINISTIC="${2:-}"; shift 2;;
    -h|--help) usage; exit 0;;
    *) echo "Unknown arg: $1" >&2; usage; exit 1;;
  esac
done

if [ -z "$ARTIFACT_ROOT" ]; then
  ARTIFACT_ROOT="$(pwd)"
fi

CLI_BIN="$ARTIFACT_ROOT/setup/dominium-setup"
MANIFEST_PATH="$ARTIFACT_ROOT/setup/manifests/product.dsumanifest"

if [ ! -x "$CLI_BIN" ]; then
  echo "Missing dominium-setup at: $CLI_BIN" >&2
  exit 1
fi
if [ ! -f "$MANIFEST_PATH" ]; then
  echo "Missing manifest at: $MANIFEST_PATH" >&2
  exit 1
fi

PLAN_PATH="${TMPDIR:-/tmp}/dominium_install.dsuplan"

cd "$ARTIFACT_ROOT"
"$CLI_BIN" --deterministic "$DETERMINISTIC" plan --manifest "$MANIFEST_PATH" --op install --scope "$SCOPE" --out "$PLAN_PATH"

if [ "$DRY_RUN" = "1" ]; then
  "$CLI_BIN" --deterministic "$DETERMINISTIC" apply --plan "$PLAN_PATH" --dry-run
else
  "$CLI_BIN" --deterministic "$DETERMINISTIC" apply --plan "$PLAN_PATH"
fi

