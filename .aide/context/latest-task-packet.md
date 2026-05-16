# AIDE Latest Task Packet

## PHASE

POST-CONVERGE-10M - Retired-Domain Path Policy Remediation

## GOAL

Reduce or classify focused RepoX retired-domain path policy failures without moving files, reintroducing old roots, creating aliases, retiring exceptions, or changing product/runtime source behavior.

## WHY

After POST-CONVERGE-10L, focused RepoX still contained stale path failures for retired embodiment, geology, worldgen, universe, and diagnostics roots. Some old paths were stale current rule assumptions; others could be legitimate historical evidence or real current policy blockers.

## CURRENT RESULT

PARTIAL. Focused `inv_repox_rules` improved from 51 failures / 5 warnings to 23 failures / 5 warnings. Safe stale RepoX rule paths were updated to exact current locations. Two current MW-4 fixture failures remain because `game.domains.embodiment` lazily imports retired `embodiment.*` modules; fixing that is a product/runtime source behavior change and was out of 10M scope.

## CONTEXT_REFS

- `docs/repo/audits/POST_CONVERGE_10M_RETIRED_DOMAIN_PATH_POLICY.md`
- `.aide/reports/POST-CONVERGE-10M-retired-domain-findings.json`
- `.aide/reports/POST-CONVERGE-10M-repox-before-after.json`
- `.aide/reports/POST-CONVERGE-10M-post-converge-11-readiness.md`
- `scripts/ci/check_repox_rules.py`

## IMPLEMENTATION

POST-CONVERGE-10M updates RepoX rule path expectations for current converged source locations and repairs RepoX group cache hashing for direct file dependencies. It preserves the remaining source import blocker as a real blocker.

## EVIDENCE

- `ctest --preset verify -N` reports 493 tests.
- Focused `ctest --preset verify -R inv_repox_rules --output-on-failure` reports 23 failures / 5 warnings after the safe fixes.
- The residual retired-domain failures reproduce through `game.domains.embodiment.__getattr__` importing retired `embodiment.*` modules.

## NON_GOALS

- no root moves, deletes, renames, aliases, move maps, or salvage maps
- no product boot proof
- no portable projection proof
- no package or release generation
- no product/runtime source behavior changes
- no RepoX/AuditX/TestX weakening

## ACCEPTANCE

- retired-domain failures are classified by rule family
- safe stale RepoX paths are fixed
- source/runtime import blockers remain blockers
- focused RepoX before/after counts are recorded
- POST-CONVERGE-11 readiness is explicit
- next family is recommended

## OUTPUT_SCHEMA

Human-readable reports plus JSON evidence:

- `.aide/reports/POST-CONVERGE-10M-retired-domain-findings.json`
- `.aide/reports/POST-CONVERGE-10M-repox-before-after.json`

## TOKEN_ESTIMATE

Latest packet is intended to stay below the AIDE compact-context budget.

## ALLOWED_PATHS

- AIDE reports/context/ledger
- post-converge and release status docs
- direct audit evidence
- RepoX rule/check implementation directly implicated by retired-domain path policy

## FORBIDDEN_PATHS

- product/runtime/source behavior changes
- generated product/projection/package/release artifacts
- root moves, deletes, renames, aliases, or move maps
- RepoX/AuditX/TestX weakening

## VALIDATION

Focused RepoX was rerun after the safe fixes and remains expected-failing at 23 failures / 5 warnings. Final command details are recorded in `.aide/reports/POST-CONVERGE-10M-validation.md`.

## NEXT

Recommended semantic task: `POST-CONVERGE-10N - Tool Hash, Audit Staleness, Ruleset Mapping, and Remaining RepoX Gate Classification`.
