#!/usr/bin/env bash
set -euo pipefail

root="$(cd "$(dirname "$0")/../.." && pwd)"
preset="${1:-debug}"

"$root/scripts/setup2/maintenance_checks.sh"

ctest --preset "$preset" -L setup2 -LE setup2_adapters -E "setup2_conformance|setup2_parity_lock_|setup2_gold_master_" --output-on-failure
ctest --preset "$preset" -R setup2_conformance --output-on-failure
ctest --preset "$preset" -R setup2_conformance_repeat --output-on-failure
ctest --preset "$preset" -R setup2_parity_lock_ --output-on-failure
ctest --preset "$preset" -R setup2_gold_master_ --output-on-failure
ctest --preset "$preset" -L setup2_adapters --output-on-failure
