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
- cause: `tools/xstack/compatx/schema_registry.py` discovered root `schemas/`, while canonical JSON schemas now live under `contracts/schemas/`.

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

- `tools/xstack/compatx/schema_registry.py` now discovers canonical `contracts/schemas/` first and retains legacy `schemas/` fallback.
- `game/domains/worldgen/mw/mw_surface_refiner_l3.py` now imports the Earth surface generator through `game.domains.worldgen.earth`.
- `scripts/ci/check_repox_rules.py` now points worldgen source-path constants at the canonical `game/domains/...` locations.

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
