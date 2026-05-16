Status: DERIVED
Last Reviewed: 2026-05-16
Supersedes: none
Superseded By: none

# POST-CONVERGE-10M Retired-Domain Path Policy Remediation

## Status

- Task ID: POST-CONVERGE-10M
- Result: PARTIAL
- Branch: `main`
- HEAD: `1def409fc17acfe4061fc3039517d892a4f0afec`
- origin/main: `ac57200b86ac14253b3fb48070acf75c35514150`
- Worktree before: clean
- Worktree after: scoped RepoX rule/evidence/status changes pending commit

## Scope

This was focused retired-domain path policy remediation. It applied no root moves, no file moves, no deletes, no renames, no path aliases, no layout exception retirement, no product proof, no portable projection proof, no package proof, no release generation, and no product/runtime source behavior changes.

## Prior State

POST-CONVERGE-10L left focused RepoX at 51 failures and 5 warnings. The remaining families included distribution/product proof blockers, retired-domain path policy checks, tool hash/audit staleness, ruleset mapping gaps, and smaller policy failures.

## Reproduction

| Command | Result | Failures | Warnings | Notes |
| --- | --- | ---: | ---: | --- |
| `ctest --preset verify -N` | PASS | 0 | 0 | Canonical verify discovery reports 493 tests. |
| `ctest --preset verify -R inv_repox_rules --output-on-failure` before | FAIL_EXPECTED | 51 | 5 | Baseline from POST-CONVERGE-10L. |
| `ctest --preset verify -R inv_repox_rules --output-on-failure` after | FAIL_EXPECTED | 23 | 5 | Stale RepoX retired-root paths fixed; source import blockers remain. |

## Retired-Domain Findings

| Family | Count | Classification | Disposition |
| --- | ---: | --- | --- |
| RepoX rule paths still pointed at retired `embodiment/`, `geo/`, `worldgen/refinement/`, `universe/`, and `diag/` roots | 28 | `stale_current_reference` | Fixed to exact current paths. |
| RepoX cache did not hash direct file dependencies | 0 | `retired_domain_rule_false_positive` | Fixed so rule edits invalidate default group cache. |
| MW-4 fixture imports reach retired `embodiment.*` lazy exports through `game.domains.embodiment` | 2 | `real_current_policy_violation` | Preserved as blockers; product/runtime source behavior change is out of scope. |

## Changes Made

- Updated `scripts/ci/check_repox_rules.py` path constants and local expectations to current converged paths under `game/domains/embodiment`, `game/domains/geology`, `game/domains/worldgen/refinement`, `game/domains/universe`, and `runtime/diagnostics`.
- Updated RepoX group cache dependency hashing so direct file dependencies such as `scripts/ci/check_repox_rules.py` contribute their file content hash.
- Added POST-CONVERGE-10M AIDE reports and audit evidence.
- Updated post-converge status docs and latest AIDE packets.

## Before/After

| Metric | Before | After |
| --- | ---: | ---: |
| Focused RepoX failures | 51 | 23 |
| Focused RepoX warnings | 5 | 5 |
| Retired-domain stale rule path failures | 28 | 0 |
| Retired-domain source import blockers | 2 | 2 |

## Remaining Blockers

- Distribution/product proof blockers from POST-CONVERGE-10L: 12 failures.
- Current `game.domains.embodiment` lazy import blocker: 2 failures.
- Tool hash/audit staleness: 3 failures plus one warning.
- Ruleset mapping gaps: 2 failures.
- Canon supersession, extension registry, worldgen retry-loop, and shadow-bound policy failures: 4 failures.
- Four glossary warnings in audit evidence.

## POST-CONVERGE-11 Readiness

POST-CONVERGE-11 is not ready. Product/projection proof failures should not circularly block POST-CONVERGE-11 on their own, but focused RepoX still contains real non-proof governance and current source import blockers.

## Validation

- `ctest --preset verify -N`: PASS, 493 tests discovered.
- `ctest --preset verify -R inv_repox_rules --output-on-failure`: FAIL_EXPECTED, 23 failures / 5 warnings after safe fixes.
- `python -m py_compile scripts/ci/check_repox_rules.py`: PASS.
- Final command details are recorded in `.aide/reports/POST-CONVERGE-10M-validation.md`.

## POST-CONVERGE-10N Follow-up

POST-CONVERGE-10N reduced focused RepoX from 23 failures / 5 warnings to 20 failures / 5 warnings by refreshing canonical identity and SecureX integrity evidence and by adding explicit docs/audit evidence dependencies to cached RepoX groups. It did not run product boot proof, portable projection proof, package proof, or release proof. POST-CONVERGE-11 remains blocked because non-proof RepoX governance/source-policy failures remain.
