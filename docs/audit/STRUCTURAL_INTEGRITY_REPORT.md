Status: DERIVED
Last Reviewed: unknown
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: DOC-CONVERGENCE
Replacement Target: canon-aligned documentation set for convergence and release preparation

# STRUCTURAL INTEGRITY REPORT

Status: Blocked  
Last Reviewed: 2026-03-04  
Pass ID: `REFACTOR-PATCH-1`

## Scope

This pass targeted governance hardening only:

- no feature additions
- no solver additions
- no intentional gameplay semantic changes
- no nondeterministic shortcuts

## Summary Of Structural Changes

1. Model purity enforcement:
- RepoX invariant `INV-REALISM-DETAIL-MUST-BE-MODEL` promoted to strict-blocking behavior.
- AuditX `E179_INLINE_RESPONSE_CURVE_SMELL` promoted to blocking severity in STRICT/FULL profiles.
- Deprecation map added for non-migrated inline curves (`7` sites) in `data/registries/deprecation_registry.json`.

2. Coupling discipline:
- Added RepoX invariant `INV-CROSS-DOMAIN-MUTATION-MUST-BE-MODEL`.
- Current STRICT scan: no blocker hits for direct ELEC->THERM / THERM->MECH mutation pattern checks.

3. Action/info grammar hardening:
- Added RepoX invariant `INV-INFO-ARTIFACT-MUST-HAVE-FAMILY`.
- Added canonical mapping registry `data/registries/info_artifact_family_registry.json` (`6` families, `8` artifact mappings).
- `INV-ACTION-MUST-HAVE-FAMILY` and `INV-INFO-ARTIFACT-MUST-HAVE-FAMILY` now evaluated in STRICT gate flow.

4. Energy/loss convention hardening:
- Added RepoX invariant `INV-LOSS-MUST-DECLARE-TARGET`.
- Thermal/loss checks now enforce explicit heat/temperature sink declaration paths.

5. Safety strictness:
- Tightened strict behavior for `INV-NO-ADHOC-SAFETY-LOGIC`.

6. Governance docs/rulesets:
- Updated `repo/repox/rulesets/core.json` with new structural invariants.
- Updated `docs/governance/REPOX_RULESETS.md` with strict-hardened rule references.

## Validation Results

### RepoX STRICT

- Command: `python tools/xstack/repox/check.py --profile STRICT`
- Artifact: `build/repox/repox_strict_refactor1.json`
- Result: `pass`
- Findings: `17` warnings, `0` strict blockers.

### AuditX STRICT

- Command: `python tools/xstack/auditx/check.py --profile STRICT`
- Artifact: `build/auditx/auditx_strict_refactor1.json`
- Result: `fail`
- Findings: `1564` total, `7` strict blockers (promoted `E179_INLINE_RESPONSE_CURVE_SMELL`).
- Blocking sites:
  - `src/fields/field_engine.py:720`
  - `src/mechanics/structural_graph_engine.py:550`
  - `src/mobility/maintenance/wear_engine.py:165`
  - `src/mobility/micro/constrained_motion_solver.py:309`
  - `src/mobility/traffic/traffic_engine.py:125`
  - `src/mobility/travel/travel_engine.py:621`
  - `src/signals/trust/trust_engine.py:346`

### TestX FULL (No Cache)

- Command: `python tools/xstack/testx/runner.py --profile FULL --cache off`
- Artifact: `build/testx/testx_full_refactor1_nocache.json`
- Result: `fail`
- Totals: `635` selected, `493` pass, `142` fail, `0` refusal.

Critical fail signals include:

- `test_determinism_envelope_full_stack`
- `testx.embodiment.thread_count_invariance_for_collision`
- `testx.reality.null_boot_deterministic`

### Stress Harnesses

Executed artifacts:

- MOB: `build/mobility/mobility_stress_report.refactor1.json`
  - fingerprint: `ba5e18781949a8c759bf3e3ac4bbb12e5db06a25aa99212452c6e097916cc62b`
- THERM: `build/thermal/therm_stress_report.refactor1.json`
  - fingerprint: `05d91a972a2b2e06a34eeb114da69ac5390e03f693739986d48fabd69eefef30`
- SIG: `build/signals/sig_stress_report.refactor1.json`
  - fingerprint: `9d23284dcf22d0eb4d704633f964d3d277d8621816b7309414efb47a06cec36d`
- ELEC: `build/electric/elec_stress_report.refactor1.json`
  - fingerprint: `c0f96b3256d87857ec4d997b77a9b060b7068aa6594ed5ac05c43ebcd355458d`

Replay hash-equivalence checks:

- SIG replay: `build/signals/sig_replay_window.refactor1.json` (`matches=true`)
- THERM replay: `build/thermal/therm_replay_window.refactor1.json` (`matches=true`)
- ELEC replay (ELEC-5 baseline window): `build/electric/elec_replay_window.refactor1.json` (`matches=true`)

## Regression Baseline Status

- No canonical baseline lockfiles were advanced in this pass.
- Stress/replay artifacts were generated for review and comparison but not promoted as new baseline authority.

## Stop Condition Evaluation

Stop conditions were triggered by FULL validation output:

- determinism regression indicated (`test_determinism_envelope_full_stack`, thread-invariance failure)
- null-boot violation indicated (`testx.reality.null_boot_deterministic`)

Given stop-condition trigger, this pass is marked **Blocked** and **not PHYS-0 ready**.

## Readiness For PHYS-0

- Governance hardening and strict invariant wiring are in place.
- Structural gate outcome remains blocked until strict inline-curve blockers and FULL determinism/null-boot failures are resolved.
