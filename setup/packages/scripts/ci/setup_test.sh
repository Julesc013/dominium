#!/usr/bin/env bash
set -euo pipefail

root="$(cd "$(dirname "$0")/../.." && pwd)"
preset="${1:-debug}"

"$root/scripts/setup/maintenance_checks.sh"

ctest --preset "$preset" -L setup -LE setup_adapters -E "setup_conformance|setup_parity_lock_|setup_gold_master_" --output-on-failure
ctest --preset "$preset" -R setup_conformance --output-on-failure
ctest --preset "$preset" -R setup_conformance_repeat --output-on-failure
ctest --preset "$preset" -R setup_parity_lock_ --output-on-failure
ctest --preset "$preset" -R setup_gold_master_ --output-on-failure
ctest --preset "$preset" -L setup_adapters --output-on-failure
