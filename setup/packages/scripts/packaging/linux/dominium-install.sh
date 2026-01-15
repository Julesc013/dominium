#!/usr/bin/env sh
set -eu

usage() {
  echo "Usage: $(basename "$0") [--artifact-root DIR] [--scope portable|user|system] [--install-root DIR]"
  echo "                         [--components CSV] [--exclude CSV] [--dry-run] [--deterministic 0|1]"
}

ARTIFACT_ROOT=""
SCOPE="portable"
INSTALL_ROOT=""
COMPONENTS=""
EXCLUDE=""
DRY_RUN="0"
DETERMINISTIC="1"

while [ $# -gt 0 ]; do
  case "$1" in
    --artifact-root) ARTIFACT_ROOT="${2:-}"; shift 2;;
    --scope) SCOPE="${2:-}"; shift 2;;
    --install-root|--path) INSTALL_ROOT="${2:-}"; shift 2;;
    --components) COMPONENTS="${2:-}"; shift 2;;
    --exclude) EXCLUDE="${2:-}"; shift 2;;
    --dry-run) DRY_RUN="1"; shift 1;;
    --deterministic) DETERMINISTIC="${2:-}"; shift 2;;
    -h|--help) usage; exit 0;;
    *) echo "Unknown arg: $1" >&2; usage; exit 1;;
  esac
done

if [ -z "$ARTIFACT_ROOT" ]; then
  ARTIFACT_ROOT="$(pwd)"
fi
ARTIFACT_ROOT="$(cd "$ARTIFACT_ROOT" && pwd)"

CLI_BIN="$ARTIFACT_ROOT/setup/dominium-setup"
ADAPTER_BIN="$ARTIFACT_ROOT/setup/dominium-setup-linux"
MANIFEST_PATH="$ARTIFACT_ROOT/setup/manifests/product.dsumanifest"

if [ ! -x "$CLI_BIN" ]; then
  echo "Missing dominium-setup at: $CLI_BIN" >&2
  exit 1
fi
if [ ! -f "$MANIFEST_PATH" ]; then
  echo "Missing manifest at: $MANIFEST_PATH" >&2
  exit 1
fi

INVOCATION_PATH="${TMPDIR:-/tmp}/dominium_install.dsuinv"
PLAN_PATH="${TMPDIR:-/tmp}/dominium_install.dsuplan"

if [ -z "$INSTALL_ROOT" ]; then
  case "$SCOPE" in
    portable) INSTALL_ROOT="$ARTIFACT_ROOT/install/portable";;
    user)
      if [ -n "${XDG_DATA_HOME:-}" ]; then
        INSTALL_ROOT="${XDG_DATA_HOME}/dominium"
      else
        INSTALL_ROOT="${HOME:-$ARTIFACT_ROOT}/.local/share/dominium"
      fi
      ;;
    system) INSTALL_ROOT="/opt/dominium";;
    *) echo "Unknown scope: $SCOPE" >&2; exit 1;;
  esac
fi

cd "$ARTIFACT_ROOT"
CMD_ARGS="--manifest \"$MANIFEST_PATH\" --op install --scope \"$SCOPE\" --install-root \"$INSTALL_ROOT\" --ui-mode cli --frontend-id tarball --out \"$INVOCATION_PATH\""
if [ -n "$COMPONENTS" ]; then
  CMD_ARGS="$CMD_ARGS --components \"$COMPONENTS\""
fi
if [ -n "$EXCLUDE" ]; then
  CMD_ARGS="$CMD_ARGS --exclude \"$EXCLUDE\""
fi

eval "\"$CLI_BIN\" --deterministic \"$DETERMINISTIC\" export-invocation $CMD_ARGS"
eval "\"$CLI_BIN\" --deterministic \"$DETERMINISTIC\" plan --manifest \"$MANIFEST_PATH\" --invocation \"$INVOCATION_PATH\" --out \"$PLAN_PATH\""

if [ "$DRY_RUN" = "1" ]; then
  "$CLI_BIN" --deterministic "$DETERMINISTIC" apply --plan "$PLAN_PATH" --dry-run
else
  "$CLI_BIN" --deterministic "$DETERMINISTIC" apply --plan "$PLAN_PATH"
  STATE_PATH="$INSTALL_ROOT/.dsu/installed_state.dsustate"
  if [ -x "$ADAPTER_BIN" ] && [ -f "$STATE_PATH" ]; then
    "$ADAPTER_BIN" platform-register --state "$STATE_PATH" --deterministic || true
  fi
fi

