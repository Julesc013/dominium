Status: DERIVED
Last Reviewed: 2026-05-18
Supersedes: none
Superseded By: none

# TEST-PERF-01 Validation

Result: PASS_WITH_WARNINGS.

## Commands Run

- `git status --short --branch`: clean at task start.
- `git fetch --all --prune`: PASS.
- `py -3 .aide/scripts/aide_lite.py doctor`: PASS.
- `py -3 .aide/scripts/aide_lite.py validate`: PASS.
- `py -3 .aide/scripts/aide_lite.py pack --task "TEST-PERF-01 CTest Sharding and AuditX Wall-Time Baseline"`: PASS.
- `py -3 .aide/scripts/aide_lite.py test`: PASS.
- `py -3 .aide/scripts/aide_lite.py selftest`: PASS.
- `py -3 .aide/scripts/aide_lite.py tools validate`: PASS.
- `py -3 .aide/scripts/aide_lite.py roots validate`: PASS.
- `py -3 .aide/scripts/aide_lite.py repo validate`: PASS.
- `python tools/validators/check_repo_layout.py --repo-root . --strict`: PASS.
- `python tools/validators/check_root_allowlist.py --repo-root . --strict`: PASS.
- `python tools/validators/check_distribution_layout.py --repo-root . --strict`: PASS.
- `python tools/validators/check_component_matrices.py --repo-root . --strict`: PASS.
- `python tools/validators/repo/check_no_src_source_dirs.py --repo-root .`: PASS_WITH_WARNINGS.
- `python tools/validators/repo/check_path_terms.py --repo-root .`: PASS_WITH_WARNINGS.
- `python tools/validators/repo/check_directory_naming.py --repo-root .`: PASS_WITH_WARNINGS.
- `python tools/validators/repo/check_file_naming.py --repo-root .`: PASS_WITH_WARNINGS.
- `python scripts/verify_docs_sanity.py --repo-root .`: PASS.
- `python scripts/verify_build_target_boundaries.py --repo-root .`: PASS.
- `python scripts/verify_ui_shell_purity.py --repo-root .`: PASS.
- `python scripts/verify_abi_boundaries.py --repo-root .`: PASS.
- `py -3 -m py_compile tools/xstack/core/impact_graph.py`: PASS.
- JSON parse for TEST-PERF-01 inventory/timing/shard/readiness reports: PASS.
- `git diff --check`: PASS.
- `git diff --cached --check`: PASS.
- `cmake --preset verify`: PASS after CTest label edits.
- `ctest --preset verify -R inv_repox_rules --output-on-failure --timeout 300`: PASS, 128.978 seconds.
- `ctest --preset verify -L smoke --output-on-failure --timeout 300`: PASS after impact fallback, 55.829 seconds.
- `ctest --preset verify -L fast --output-on-failure --timeout 300`: PASS, 48.821 seconds.
- `ctest --preset verify -L audit --output-on-failure --timeout 1200`: PASS, 824.573 seconds.
- `ctest --preset verify -R slice0_hardcoded_ids --output-on-failure --timeout 300`: FAIL, expected semantic lint blocker.
- `ctest --preset verify -R slice1_hardcoded_constants --output-on-failure --timeout 300`: FAIL, expected semantic lint blocker.

## Not Run

- Full monolithic CTest was not run. TEST-PERF-01 makes the suite shardable and records that full CTest remains semantically blocked by `slice0_hardcoded_ids` and `slice1_hardcoded_constants`.
- `cmake --build --preset verify` was not run. This task changed CTest labels/timeouts and a Python impact fallback; `cmake --preset verify` regenerated CTest metadata successfully and no binary source changed.
- Full eval, package generation, release generation, and public release flows were not run.
