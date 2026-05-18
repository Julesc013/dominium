Status: PASS_WITH_WARNINGS
Last Reviewed: 2026-05-18
Task: MOVE-ROUTER-01

# MOVE-ROUTER-01 Apply Bad-Root Router Audit

## Scope

MOVE-ROUTER-01 physically applied the deterministic bad-root route table created
by MOVE-ROUTER-00. The task used `git mv` for tracked files and did not edit the
contents of moved files.

## Inputs

- `contracts/repo/naming.contract.toml`
- `contracts/repo/bad_root_routing.contract.toml`
- `tools/migration/route_bad_roots.py`
- `.aide/reports/MOVE-ROUTER-01-preapply-route-table.json`

## Result

| Metric | Count |
| --- | ---: |
| Bad-root tracked files before | 1,765 |
| Bad-root tracked files after | 0 |
| Files moved | 1,765 |
| Semantic moves | 1,694 |
| Quarantine moves | 71 |
| Skipped moves | 0 |
| Target collisions | 0 |
| Roots emptied | 24 |

## Exception Actions

The 23 active bad-root directory exceptions were moved to the existing
`retired_exceptions` ledger namespace in `contracts/repo/layout_exceptions.toml`
after `git ls-files <root>` returned zero for each former bad root. `ide/` was
already retired and remained empty.

Untracked `__pycache__/*.pyc` leftovers under empty former-root directories were
removed after verifying they were generated local files and no tracked file
remained under those roots.

## Stale References

MOVE-ROUTER-01 intentionally did not perform broad reference or import repair.
The stale-reference scan is recorded in:

`.aide/reports/MOVE-ROUTER-01-stale-reference-scan.json`

Repair is assigned to:

`MOVE-ROUTER-02 - Repair References, Imports, Build, Projection, and Exceptions After Routing`

## Non-Goals

- No feature work.
- No semantic ID mutation.
- No package/profile/bundle identity mutation.
- No release, projection, installer, tag, upload, or GitHub release.
- No CMake or product boot repair.

## Validation

- PASS: AIDE doctor/validate/test/selftest/tools/roots/repo.
- PASS: strict repo layout, root allowlist, distribution layout, component
  matrix validators.
- PASS: bad-root absence validator with zero tracked former-root files.
- PASS: docs sanity, build target boundaries, UI shell purity, ABI boundaries,
  and `git diff --check`.
- WARN: stale references/imports/build paths remain assigned to MOVE-ROUTER-02.
