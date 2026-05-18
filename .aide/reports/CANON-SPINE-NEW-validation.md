# CANON-SPINE-NEW Validation

## Passed

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
- `python tools/validators/repo/check_no_src_source_dirs.py --repo-root .`
- `python tools/validators/repo/check_forbidden_root_names.py --repo-root .`
- `python scripts/verify_docs_sanity.py --repo-root .`
- `python scripts/verify_ui_shell_purity.py --repo-root .`
- `python scripts/verify_abi_boundaries.py --repo-root .`
- `python scripts/verify_includes_sanity.py`
- `cmake --preset verify`
- `ctest --preset verify -L smoke --output-on-failure --timeout 300`
- focused spine CTest lane covering capability inspect, setup install, UI bind, platform, renderer, and command surface tests.
- `python -m py_compile` over changed Python files.

## Warnings / Not Green

- `python scripts/verify_build_target_boundaries.py --repo-root .` fails with existing boundary warnings in runtime UI/platform and tool imports.
- Full verify CTest remains red outside the smoke/focused spine lane.
- `check_no_src_source_dirs.py` and `check_forbidden_root_names.py` pass with warning/info debt from archive and fixtures.

## Not Run

- Public release generation.
- GitHub release/tag/upload work.
- Full release projection generation.
