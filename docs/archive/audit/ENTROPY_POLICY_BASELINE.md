Status: DERIVED
Last Reviewed: 2026-03-16
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: DOC-CONVERGENCE
Replacement Target: canon-aligned documentation set for convergence and release preparation

# Entropy Policy Baseline

Status: CANONICAL
Last Updated: 2026-03-04
Scope: PHYS-4 completion baseline for deterministic entropy and irreversibility hooks.

## 1) Entropy Accumulation Rules

Canonical substrate added:

- `entropy_state_rows`
- `entropy_event_rows`
- `entropy_reset_events`
- `entropy_effect_rows`

Deterministic chains added:

- `entropy_hash_chain`
- `entropy_reset_events_hash_chain`

Accumulation is registered and transformation-linked through `entropy_contribution_registry`.

## 2) Effect Policies

Registry:

- `entropy_effect.basic_linear`
- `entropy_effect.none`
- `entropy_effect.strict`

Runtime evaluation outputs:

- efficiency multipliers
- hazard multipliers
- maintenance-interval modifiers

## 3) Integration Summary

Integrated domains/processes:

- PHYS-3 energy transforms now trigger entropy contribution checks.
- ELEC loss transform path contributes entropy through registered source mapping.
- THERM phase transform (`process.material_transform_phase`) contributes entropy via phase-change stub mapping.
- MECH deformation/fracture (`process.drill_hole`, `process.mechanics_fracture`) contributes entropy via plastic-deformation mapping.
- maintenance decay now derives degradation effects from entropy effect policy outputs.
- maintenance perform triggers explicit entropy reset logging.

## 4) Proof and Replay Coverage

Control proof surfaces extended with:

- `entropy_hash_chain`
- `entropy_reset_events_hash_chain`

Server-authoritative and SRZ proof emitters now include both chains from authoritative state.

## 5) Enforcement Readiness

RepoX invariants:

- `INV-ENTROPY-UPDATE-THROUGH-ENGINE`
- `INV-NO-SILENT-EFFICIENCY-DROP`

AuditX analyzers:

- `E214_INLINE_DEGRADATION_SMELL`
- `E215_ENTROPY_BYPASS_SMELL`

## 6) FLUID-0 Readiness

PHYS-4 baseline now supplies:

- deterministic irreversibility tracking substrate,
- explicit reset semantics,
- profile-governed degradation policy hooks,
- proof/replay-compatible entropy witnesses.

This is sufficient to attach FLUID/CHEM irreversible processes without ad hoc entropy logic.

## 7) Gate Run Status (2026-03-04)

Executed commands:

- `python tools/xstack/repox/check.py --profile STRICT` -> `PASS` (no refusal findings)
- `python tools/xstack/auditx/check.py --profile STRICT` -> `FAIL` (`promoted_blockers=7`, all `E179_INLINE_RESPONSE_CURVE_SMELL`, pre-existing outside PHYS-4 paths)
- `python tools/xstack/testx/runner.py --profile STRICT --cache off` -> `FAIL` (pre-existing global suite failures outside PHYS-4 scope)
- `python tools/xstack/run.py strict --repo-root . --cache on` -> `REFUSAL` (CompatX/session boot/AuditX/TestX/packaging baseline failures)
- `python tools/xstack/testx/runner.py --profile FAST --subset test_entropy_increment_deterministic,test_entropy_monotonic_without_reset,test_maintenance_reduces_entropy_logged,test_efficiency_degrades_with_entropy,test_cross_platform_entropy_hash` -> `PASS`

PHYS-4 entropy substrate changes are validated by the targeted entropy tests and strict RepoX, while global repository strict gates still include pre-existing blockers.
