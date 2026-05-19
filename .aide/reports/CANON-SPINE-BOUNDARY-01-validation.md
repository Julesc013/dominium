# CANON-SPINE-BOUNDARY-01 Validation

## PASS

- `py -3 .aide/scripts/aide_lite.py doctor`
- `py -3 .aide/scripts/aide_lite.py validate`
- `py -3 .aide/scripts/aide_lite.py test`
- `py -3 .aide/scripts/aide_lite.py selftest`
- `py -3 .aide/scripts/aide_lite.py tools validate`
- `py -3 .aide/scripts/aide_lite.py roots validate`
- `py -3 .aide/scripts/aide_lite.py repo validate`
- `python tools/validators/check_repo_layout.py --repo-root . --strict`
- `python tools/validators/check_root_allowlist.py --repo-root . --strict`
- `python tools/validators/check_distribution_layout.py --repo-root . --strict`
- `python tools/validators/check_component_matrices.py --repo-root . --strict`
- `python tools/validators/repo/check_bad_root_absence.py --repo-root . --json`
- `python scripts/verify_build_target_boundaries.py`
- `python scripts/verify_docs_sanity.py --repo-root .`
- `python scripts/verify_ui_shell_purity.py --repo-root .`
- `python scripts/verify_abi_boundaries.py --repo-root .`
- `python scripts/verify_includes_sanity.py`
- `python -m py_compile` on touched Python modules
- `cmake --preset verify`
- `cmake --build --preset verify --target ALL_BUILD`
- `ctest --preset verify -L smoke --output-on-failure --timeout 300` (57/57)
- `ctest --preset verify -R "tools_capability_inspect|setup_install_tests|app_ui_bind_phase|capability_matrix_capset_world_nonbio_test_command_surface|platform_contract_tests|renderer_contract_tests" --output-on-failure --timeout 300` (6/6)

## PASS_WITH_WARNINGS

- `python tools/validators/repo/check_no_src_source_dirs.py --repo-root .`: 0 blockers, historical/archive info findings only.
- `python tools/validators/repo/check_forbidden_root_names.py --repo-root .`: 0 blockers, archive/fixture warning debt remains.
- AIDE validate warns that the repo map source snapshot hash is stale.

## NOT GREEN

- `cmake --build --preset verify` invokes the full verification custom target and exits nonzero because the full CTest lane is still not green.
- Full verify CTest latest observed result before final include repairs: 231/344 passed, 113 failed.
