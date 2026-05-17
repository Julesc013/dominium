# RESTRUCTURE-REPAIR-00 Validation

## Passing Gates

- `py -3 .aide/scripts/aide_lite.py doctor`: PASS.
- `py -3 .aide/scripts/aide_lite.py validate`: PASS.
- `py -3 .aide/scripts/aide_lite.py test`: PASS.
- `py -3 .aide/scripts/aide_lite.py selftest`: PASS.
- `py -3 .aide/scripts/aide_lite.py tools validate`: PASS.
- `py -3 .aide/scripts/aide_lite.py roots validate`: PASS.
- `py -3 .aide/scripts/aide_lite.py repo validate`: PASS.
- `python tools/validators/check_repo_layout.py --repo-root . --strict`: PASS.
- `python tools/validators/check_root_allowlist.py --repo-root . --strict`: PASS.
- `python tools/validators/check_distribution_layout.py --repo-root . --strict`: PASS.
- `python tools/validators/check_component_matrices.py --repo-root . --strict`: PASS.
- `python scripts/verify_docs_sanity.py --repo-root .`: PASS.
- `python scripts/verify_build_target_boundaries.py --repo-root .`: PASS.
- `python scripts/verify_ui_shell_purity.py --repo-root .`: PASS.
- `python scripts/verify_abi_boundaries.py --repo-root .`: PASS.
- `ctest --preset verify -R inv_repox_rules --output-on-failure --timeout 300`: PASS.
- `ctest --preset verify -L smoke --output-on-failure --timeout 300`: PASS, 57/57 tests.
- `cmake --preset verify`: PASS with existing SDL2/PkgConfig warnings.
- `cmake --build --preset verify --target ALL_BUILD`: PASS.
- `python tests/contract/frozen_contracts_guard.py --repo-root .`: PASS after hash evidence refresh.
- `python tests/invariant/override_policy_tests.py --repo-root .`: PASS after expired overrides were removed.
- `python tests/determinism/determinism_replay_hash_invariance.py --repo-root .`: PASS after replay fixture hashes were refreshed.
- `python tools/validators/check_product_boot_matrix.py --repo-root . --json --strict --run-smoke --timeout 30`: PASS.
- `python tools/validators/check_portable_projection.py --repo-root . --projection-root .dominium.local/projections/post-converge-12/v0.0.0-post-converge-12/win64/dominium --json --strict`: PASS.
- `python tools/validators/check_internal_pilot_release.py --repo-root . --release-root .dominium.local/releases/internal-pilot-0 --json --strict`: PASS.
- `py -3 -m py_compile tools/auditx/graph/builder.py tools/auditx/cache_engine.py tools/release/archive_policy_common.py tools/auditx/analyzers/e536_missing_archive_record_smell.py tools/auditx/analyzers/e537_overwritten_release_index_smell.py`: PASS.

## Focused CTest Status

The focused repair set for previously fixed stale-path/archive/hash/override/replay failures now passes the repaired direct checks. The combined CTest focus:

`ctest --preset verify -R slice0_hardcoded_ids|slice1_hardcoded_constants|const_frozen_contract_hashes|inv_override_policy|determinism_replay_hash_invariance --output-on-failure --timeout 300`

passed `const_frozen_contract_hashes`, `inv_override_policy`, and `determinism_replay_hash_invariance`, and still failed `slice0_hardcoded_ids` and `slice1_hardcoded_constants`.

## Remaining Failing Or Incomplete Gates

- Full `ctest --preset verify --output-on-failure --timeout 300`: not green; rerun is blocked by known semantic lint failures and AuditX wall-time.
- `slice0_hardcoded_ids`: still fails on current domain/source/tool/test identifiers. This needs doctrine-backed disposition, not a broad allowlist.
- `slice1_hardcoded_constants`: still fails on current atmosphere/gravity/oxygen assumptions. This needs semantic remediation or an explicit contract decision.
- `tools_auditx`: still exceeds the 300 second CTest timeout. The static archive-policy child process was removed from the AuditX analyzer path, but the full AuditX CTest still needs partitioning/performance work.
- Prior commits `51257dfdb` and `0a579e3c` remain historical commit-policy warnings and were not amended.

## Build Note

The pure build target `ALL_BUILD` completed successfully and produced the expected native binaries. The broader default verify build remains unsuitable as a pure build proof because it enters validation/test lanes that include known wall-time blockers.
