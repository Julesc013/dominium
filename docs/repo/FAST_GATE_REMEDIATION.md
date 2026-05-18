Status: DERIVED
Last Reviewed: 2026-05-16
Supersedes: none
Superseded By: none

# FAST Gate Remediation

## Status

- Phase: POST-CONVERGE-10G
- Current status: partial, RepoX reduced but still blocking

## Command

```text
python scripts/dev/gate.py verify --repo-root .
```

## Current Failure

Initial POST-CONVERGE-06 reproduction:

- result: fail
- runner: `repox_runner`
- XStack failure class: `STRUCTURAL`
- concrete exception: `ValueError: invalid mod policy registry`
- cause: `tools/xstack/compatx/schema_registry.py` discovered root `schemas/`, while canonical JSON schemas now live under `contracts/schema/`.

After remediation:

- `modding.load_mod_policy_registry('.')`: pass, 3 policies loaded.
- direct RepoX command: fail with 1800 failures and 5 warnings.
- XStack FAST command: fail with primary failure class `DRIFT`.

## Classification

- original blocker: `stale_path_after_convergence`
- remediated by this task: yes
- remaining FAST state: broad RepoX drift backlog, not safe for POST-CONVERGE-06 broad remediation

## Remediation

Fixed:

- `tools/xstack/compatx/schema_registry.py` now discovers canonical `contracts/schema/` first and retains legacy `schemas/` fallback.
- `game/domain/worldgen/mw/mw_surface_refiner_l3.py` now imports the Earth surface generator through `game.domain.worldgen.earth`.
- `scripts/ci/check_repox_rules.py` now points worldgen source-path constants at the canonical `game/domain/...` locations.

Remaining:

- RepoX now reports broad drift, including stale canonical-doc index entries, missing generated distribution descriptors, stale AppShell/embodiment/geo path assumptions, generated audit drift, rule-map gaps, and root-structure drift.
- These are not safe to resolve as part of POST-CONVERGE-06 without broad RepoX, AppShell, distribution, and generated-evidence remediation.
- POST-CONVERGE-10E fixed targeted AuditX path assumptions exposed by CTest, but it did not fix broad RepoX drift.
- Canonical CTest now exposes the same drift through `inv_repox_rules`.
- FAST pass is not claimed because `python scripts/dev/gate.py verify --repo-root .` was not rerun to completion and RepoX drift remains active.
- POST-CONVERGE-10F fixed the separate `invariant_units_present` blocker and classified the current RepoX proof manifest: 1,844 failures and 5 warnings remain, dominated by doc status headers, canon index drift, historical-reference drift, offline boot/AppShell gaps, and top-level structure drift.
- The focused RepoX CTest wrapper now writes generated proof/profile output to `.dominium.local/ctest/repox/` so remediation runs do not dirty tracked audit evidence.

## Follow-up

Run a targeted RepoX drift remediation task after build toolchain status is resolved. That task should separate:

- stale path references left from prior convergence moves
- missing generated distribution/build artifacts
- stale audit evidence
- intentionally absent roots that need updated RepoX rules or exemptions
- real invariant regressions that require product/runtime review
- canonical `verify` CTest discovery currently reporting 0 tests while the tuple verify build reports 493 tests
- full CTest wall-time after RepoX semantic failures are clear

## POST-CONVERGE-10G Update

POST-CONVERGE-10G reduced direct/focused RepoX from 1844 failures to 1769 failures while keeping the 5 known warnings. The safe fixes were limited to stale top-level root allowlist handling, stale root-level AppShell paths, and RepoX cache invalidation for rule implementation changes.

FAST is still not green. The remaining blocker is broad canonical documentation/status/index and policy evidence drift rather than the retired AppShell or root-structure families fixed here.

## POST-CONVERGE-10H Update

POST-CONVERGE-10H reduced RepoX from 1769 failures to 153 failures by repairing safe documentation status metadata and canon-index drift. FAST remains blocked because focused RepoX still fails, now dominated by historical/archive reference debt and smaller policy-specific families.

## POST-CONVERGE-10I Update - Historical Reference Remediation

- Result: PARTIAL.
- Focused RepoX improved from 153 failures / 5 warnings to 71 failures / 5 warnings.
- `INV-CANON-NO-HIST-REF` reduced from 81 to 0 by aligning RepoX enforcement to canonical-doc scope and preserving DERIVED quarantine/archive evidence references.
- POST-CONVERGE-11 remains blocked.
- Next recommended task: `POST-CONVERGE-10J - Authority-Sensitive Documentation Status Review`.

## POST-CONVERGE-10J Update - Authority Documentation Status

- Result: PARTIAL.
- Focused RepoX improved from 71 failures / 5 warnings to 60 failures / 5 warnings.
- `INV-DOC-STATUS-HEADER` reduced from 12 to 0.
- FAST remains blocked because focused tuple `inv_repox_rules` still fails on contract registry, product proof, retired-domain path policy, tool hash/audit staleness, and related families.
- Next recommended task: `POST-CONVERGE-10K - Contract Registry Acceptance Backlog Remediation`.

## POST-CONVERGE-10K Update - Contract Registry Acceptance

- Result: PARTIAL.
- Focused RepoX actual local state improved from 59 failures / 5 warnings to 51 failures / 5 warnings.
- The prior 10J-reported 60th failure was `INV-LOCKLIST-FROZEN`, which was absent at 10K start because `origin/main` equaled local HEAD.
- `INV-NEW-CONTRACT-REQUIRES-ENTRY` reduced from 9 to 0 by adding four accepted current architecture contract rows to `contracts/registry/semantic_contract_registry.json`.
- POST-CONVERGE-11 remains blocked because focused tuple `inv_repox_rules` still fails on distribution/product proof, retired-domain path policy, tool hash/audit staleness, ruleset mapping, and related families.
- Next recommended task: `POST-CONVERGE-10L - Distribution Descriptor and Product Proof Blocker Classification`.

## TEST-PERF-00 Update - Fast Validation Tiers

- Result: PASS_WITH_WARNINGS.
- Fast validation is now represented by `tests/validation_tiers.json` and `python scripts/test_tier.py --tier t0`.
- Impacted validation can be selected with `python scripts/test_impacted.py --from HEAD~1`.
- Canonical CTest discovery is not inherently broken; it requires a configured verify build tree. `cmake --preset verify` restored `ctest --preset verify -N` to 493 tests locally.
- CTest smoke labels now work after reconfigure; `ctest --preset verify -N -L smoke` reports 57 tests.
- FAST remains blocked as a promotion signal because focused RepoX still fails, but normal task feedback no longer needs to default to full CTest.

## POST-CONVERGE-10L Update - Distribution/Product Proof Classification

- Result: PARTIAL.
- Focused RepoX is 51 failures / 5 warnings after repairing a transient missing status header in the POST-CONVERGE-10K audit report.
- The target distribution/product proof failures are classified, not fixed: missing `archive/generated/dist/bin` wrapper/projection surfaces remain for product descriptor emission and AppShell-owned delegation.
- FAST remains blocked because non-proof RepoX failures still exist, including retired-domain path policy checks, tool hash/audit staleness, and ruleset mapping gaps.
- Next recommended semantic task: `POST-CONVERGE-10M - Retired-Domain Path Policy and Tool Hash Drift Remediation`.

## POST-CONVERGE-10M Update - Retired-Domain Path Policy

- Result: PARTIAL.
- Focused RepoX improved from 51 failures / 5 warnings to 23 failures / 5 warnings.
- The stale missing-file failures for retired `embodiment/`, `geo/`, `worldgen/refinement/`, `universe/`, and `diag/` RepoX rule paths are fixed.
- FAST remains blocked because focused RepoX still fails on distribution/product proof blockers, a current `game.domain.embodiment` lazy import blocker, tool hash/audit staleness, ruleset mapping gaps, and smaller policy failures.
- Next recommended semantic task: `POST-CONVERGE-10N - Tool Hash, Audit Staleness, Ruleset Mapping, and Remaining RepoX Gate Classification`.

## POST-CONVERGE-10N Update - Tool Hash and Audit Staleness

- Result: PARTIAL.
- Focused RepoX improved from 23 failures / 5 warnings to 20 failures / 5 warnings.
- Stale identity fingerprint and SecureX tool-hash evidence are fixed.
- FAST remains blocked because focused RepoX still fails on distribution/product proof blockers, MW-4 lazy import source-policy failures, ruleset mapping gaps, canon supersession, extension registry, worldgen retry-loop, and shadow-bound policy failures.
- The AuditX stale-output warning remains because broad AuditX regeneration was out of scope.
- Next recommended semantic task: focused residual RepoX governance/source-policy remediation or explicit RepoX acceptance gate. TEST-PERF follow-up remains appropriate for validation speed.

## POST-CONVERGE-10O Update - Closeout Gate

- Result: PARTIAL.
- Focused RepoX remains 20 failures / 5 warnings.
- Canonical `ctest --preset verify -N` reports 493 tests, so CTest discovery is not the immediate FAST blocker.
- FAST remains blocked as a promotion signal because real non-proof RepoX governance/source-policy failures remain.
- The next semantic task is `POST-CONVERGE-10P - Residual RepoX Governance and Source-Policy Remediation`.

## POST-CONVERGE-11 Update - Product Boot Gate

- Result: BLOCKED.
- POST-CONVERGE-11 stopped before product boot because focused RepoX still fails with 20 failures / 5 warnings.
- No product binaries were run and no command-surface fixes were attempted.
- FAST remains blocked by real non-proof RepoX governance/source-policy failures.
- The next semantic task remains `POST-CONVERGE-10P - Residual RepoX Governance and Source-Policy Remediation`.

## Closeout Remediation Update

- Result: PASS_WITH_WARNINGS.
- Focused RepoX is no longer the FAST blocker: direct RepoX and CTest focused `inv_repox_rules` pass.
- CTest smoke is green at 57/57 after `verify_fast` was wired to build the required product/tool binaries.
- Native product smoke is green for the five product shells on help/version/status/smoke commands.
- Remaining FAST concern is wall-time/process-control, not semantic RepoX: the full `cmake --build --preset verify` lane timed out during verification and needs TEST-PERF sharding/partition work.
- Portable projection proof remains unrun and is the next release-readiness gate.
