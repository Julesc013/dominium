#!/usr/bin/env sh
set -eu

SCRIPT_DIR="$(CDPATH= cd -- "$(dirname "$0")" && pwd)"
REPO_ROOT="$(CDPATH= cd -- "$SCRIPT_DIR/../.." && pwd)"

EXPORTS="$(python3 "$SCRIPT_DIR/env_tools.py" --repo-root "$REPO_ROOT" export --shell sh)"
status=$?
if [ "$status" -ne 0 ]; then
    printf '%s\n' "$EXPORTS"
    exit "$status"
fi
eval "$EXPORTS"

python3 "$SCRIPT_DIR/env_tools.py" --repo-root "$REPO_ROOT" doctor --require-path
