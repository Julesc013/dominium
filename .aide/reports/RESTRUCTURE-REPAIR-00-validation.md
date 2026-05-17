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
- `ctest --preset verify -R inv_repox_rules --output-on-failure`: PASS.
- `ctest --preset verify -L smoke --output-on-failure --timeout 300`: PASS, 57/57 tests.
- `cmake --preset verify`: PASS with existing SDL2/PkgConfig warnings.
- `cmake --build --preset verify --target ALL_BUILD`: PASS.
- Product boot matrix strict smoke: PASS.
- Portable projection strict validator: PASS.
- Internal pilot strict validator: PASS.

## Repaired Focused Tests

After repairs, this focused set passed 6/6:

`ctest --preset verify -R "integration_meta|path_hygiene_contracts|harden1_docs_contracts|scale0_interest_pattern_invariance|const_archive_presence|inv_archive_presence" --output-on-failure --timeout 300`

## Remaining Failing Gates

- `py -3 .aide/scripts/aide_lite.py commit check --latest` after commit `51257dfdb`: FAIL because the commit body used plain section labels instead of required `##` headings and omitted `AIDE-Token-Impact`.
- `py -3 .aide/scripts/aide_lite.py commit check --latest` after commit `0a579e3c`: FAIL because the changelog section used lowercase category prefixes instead of the required machine-readable category names.
- Full `ctest --preset verify --output-on-failure --timeout 300`: incomplete and failing. It was stopped after repeated 300-second AuditX timeouts.
- `slice0_hardcoded_ids`: still fails on hardcoded current domain identifiers, now with deterministic diagnostic output.
- `slice1_hardcoded_constants`: still fails on atmosphere/gravity/oxygen assumptions.
- `const_frozen_contract_hashes`: still fails on frozen contract hash drift.
- `inv_override_policy`: still fails on expired override entries.
- `determinism_replay_hash_invariance`: still fails on replay hash mismatches for performance profiles.
- `tools_auditx`, `test_auditx_canonical_hash_stability`, and `test_auditx_empty_path`: full CTest observed 300-second timeouts.

## Build Note

The default `cmake --build --preset verify` target invokes broad verification and failed after validation/test timeouts. The build-only target `ALL_BUILD` completed successfully and produced the expected native binaries.

## Post-Commit Policy Note

The first two repair evidence commits are retained without amendment to preserve history. The latest follow-up evidence commit uses the required commit-message schema.
