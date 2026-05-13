# FAST Gate Remediation

## Status

- Phase: POST-CONVERGE-10E
- Current status: partial

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

## Follow-up

Run a targeted RepoX drift remediation task after build toolchain status is resolved. That task should separate:

- stale path references left from prior convergence moves
- missing generated distribution/build artifacts
- stale audit evidence
- intentionally absent roots that need updated RepoX rules or exemptions
- real invariant regressions that require product/runtime review
- the current CTest `invariant_units_present` failure, which is separate from FAST but blocks native CTest proof
