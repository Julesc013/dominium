# BASELINE-00 Required Regression Commands

Status: DERIVED
Last Reviewed: 2026-05-17

## Tier 0 - Required After Every Move Family

```text
py -3 .aide/scripts/aide_lite.py doctor
py -3 .aide/scripts/aide_lite.py validate
py -3 .aide/scripts/aide_lite.py test
py -3 .aide/scripts/aide_lite.py selftest
py -3 .aide/scripts/aide_lite.py tools validate
py -3 .aide/scripts/aide_lite.py roots validate
py -3 .aide/scripts/aide_lite.py repo validate
py -3 .aide/scripts/aide_lite.py commit check --latest
python tools/validators/check_repo_layout.py --repo-root . --strict
python tools/validators/check_root_allowlist.py --repo-root . --strict
python tools/validators/check_distribution_layout.py --repo-root . --strict
python tools/validators/check_component_matrices.py --repo-root . --strict
python scripts/verify_docs_sanity.py --repo-root .
python scripts/verify_build_target_boundaries.py --repo-root .
python scripts/verify_ui_shell_purity.py --repo-root .
python scripts/verify_abi_boundaries.py --repo-root .
git status --short --branch
git diff --check
```

Also confirm generated release/projection/build/local roots remain ignored and untracked.

## Tier 1 - Medium-Risk Docs/Tooling Moves

```text
ctest --preset verify -R inv_repox_rules --output-on-failure
ctest --preset verify -L smoke --output-on-failure --timeout 300
```

Run affected AIDE wrapper commands when a wrapper or wrapper-owned evidence path is touched.

## Tier 2 - Content/Package/Profile/Bundle Moves

```text
python tools/validators/check_portable_projection.py --repo-root . --projection-root .dominium.local/projections/post-converge-12/v0.0.0-post-converge-12/win64/dominium --strict
python tools/validators/check_internal_pilot_release.py --repo-root . --release-root .dominium.local/releases/internal-pilot-0 --strict
ctest --preset verify -L smoke --output-on-failure --timeout 300
```

Run pack/profile/content validators when present and relevant.

## Tier 3 - Core/Control/Net/Lib/Runtime/Build-Sensitive Moves

```text
cmake --preset verify
cmake --build --preset verify
ctest --preset verify -L smoke --output-on-failure --timeout 300
```

Add focused CTest for the touched area, then refresh product boot proof, portable projection proof, and internal pilot release proof.

## Tier 4 - Final Post-Restructure Proof

Run full or accepted-sharded CTest, post-restructure layout audit, native build proof, product boot proof, portable projection proof, and internal pilot rebuild plus strict validation.

## Comparison Rule

Future MOVE-FAMILY proof tasks compare their after-state against BASELINE-00. Required tiers must not regress. Warning-only baseline conditions may remain warning-only only if they are not worse and remain explicitly recorded.
