#!/usr/bin/env sh
set -e

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"

cmake -P "$ROOT/scripts/setup/schema_freeze_check.cmake"

