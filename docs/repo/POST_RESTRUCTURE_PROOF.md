Status: DERIVED
Last Reviewed: 2026-05-18
Supersedes: none
Superseded By: none

# Post-Restructure Proof

Latest proof state: PARTIAL after `POST-RESTRUCTURE-REPAIR-SEMANTIC-LINTS`, `TEST-PERF-01`, and NAME-00 naming-law follow-up.

## Passing Proof Surfaces

- AIDE doctor/validate/test/selftest/tools/roots/repo.
- Strict layout/root/distribution/component validators.
- Supplemental docs/build/UI/ABI checks.
- Focused RepoX.
- Smoke CTest.
- Fast CTest label.
- Semantic lint CTest lanes.
- AuditX slow shard.
- Native configure and build-only `ALL_BUILD`.
- Product boot matrix strict smoke.
- Portable projection strict validation.
- Internal pilot release strict validation.
- Frozen contract hash guard.
- Override policy tests.
- Replay hash invariance.

## Remaining Blockers

- Full CTest is not green.
- 23 formerly bad roots remain under active exceptions with 1,764 tracked files.
- AuditX CTest wall-time is now partitioned into explicit `audit`/`auditx`/`slow`/`nightly` shards with 1200 second timeout.
- Large file-quality ledger storage policy remains unresolved.
- Naming conflicts are classified by NAME-00, but no naming migration has been applied.

## Rerun Commands

```powershell
py -3 .aide/scripts/aide_lite.py doctor
py -3 .aide/scripts/aide_lite.py validate
py -3 .aide/scripts/aide_lite.py test
py -3 .aide/scripts/aide_lite.py selftest
py -3 .aide/scripts/aide_lite.py tools validate
py -3 .aide/scripts/aide_lite.py roots validate
py -3 .aide/scripts/aide_lite.py repo validate
python tools/validators/check_repo_layout.py --repo-root . --strict
python tools/validators/check_root_allowlist.py --repo-root . --strict
python tools/validators/check_distribution_layout.py --repo-root . --strict
python tools/validators/check_component_matrices.py --repo-root . --strict
python tools/validators/repo/check_no_src_source_dirs.py --repo-root .
python tools/validators/repo/check_path_terms.py --repo-root .
python tools/validators/repo/check_directory_naming.py --repo-root .
python tools/validators/repo/check_file_naming.py --repo-root .
ctest --preset verify -R inv_repox_rules --output-on-failure --timeout 300
ctest --preset verify -R "slice0_hardcoded_ids|slice1_hardcoded_constants" --output-on-failure --timeout 300
ctest --preset verify -L smoke --output-on-failure --timeout 300
ctest --preset verify -L fast --output-on-failure --timeout 300
ctest --preset verify -L audit --output-on-failure --timeout 1200
ctest --preset verify -L slow --output-on-failure --timeout 1200
cmake --preset verify
cmake --build --preset verify --target ALL_BUILD
python tools/validators/check_product_boot_matrix.py --repo-root . --json --strict --run-smoke --timeout 30
python tools/validators/check_portable_projection.py --repo-root . --projection-root .dominium.local/projections/post-converge-12/v0.0.0-post-converge-12/win64/dominium --json --strict
python tools/validators/check_internal_pilot_release.py --repo-root . --release-root .dominium.local/releases/internal-pilot-0 --json --strict
```

## Readiness

DOE-00 is not authorized. Feature implementation remains blocked.

Next task: `MOVE-SCRIPT-00 - Generate Deterministic Bad-Root Router and Dry-Run Move Plan`.

## Semantic Lint Proof Note

POST-RESTRUCTURE-REPAIR-SEMANTIC-LINTS reproduced 1,104 hardcoded identifier/constant findings and classified every finding before allowing it. The focused lanes now pass through exact-match allowlist entries keyed by test, file, line, validator message, and source-line hash. No broad suppressions were added.

## NAME-00 Naming Proof Note

NAME-00 locks naming law and produces warning-only conflict evidence. It does not make current excepted bad roots clean, and it does not authorize `runtime/appshell -> runtime/shell`, `game/domains -> game/domain`, or contract-category singularization. Those are planned future migrations requiring reviewed scope.
