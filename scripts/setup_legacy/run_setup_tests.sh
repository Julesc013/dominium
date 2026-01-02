#!/usr/bin/env sh
set -eu

PRESET="${1:-debug}"

cmake --preset "${PRESET}"
cmake --build --preset "${PRESET}"
ctest --preset "${PRESET}" --output-on-failure -R "^(dsu_|test_)"
