Status: DERIVED
Last Reviewed: 2026-03-16
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: DOC-CONVERGENCE
Replacement Target: canon-aligned documentation set for convergence and release preparation

# PHYSICS CONSTITUTION BASELINE (PHYS-0)

Date: 2026-03-04  
Scope: PHYS-0 constitution freeze over quantities, invariants, profile/exception schemas, enforcement scaffolding, proof/replay hooks, RWAM + grammar alignment.

## 1. Canonical Quantity Baseline

Normative PHYS quantity set registered and dimensioned:

- `quantity.mass` (`dim.mass`)
- `quantity.momentum_linear` (`dim.momentum_linear`)
- `quantity.momentum_angular` (`dim.angular_momentum`)
- `quantity.force` (`dim.force`)
- `quantity.torque` (`dim.torque`)
- `quantity.energy_kinetic` (`dim.energy`)
- `quantity.energy_potential` (`dim.energy`)
- `quantity.energy_thermal` (`dim.energy`)
- `quantity.energy_electrical` (`dim.energy`)
- `quantity.energy_chemical` (`dim.energy`)
- `quantity.energy_total` (`dim.energy`)
- `quantity.heat_loss` (`dim.power`)
- `quantity.entropy_index` (`dim.dimensionless`)
- `quantity.radiation_dose` (`dim.specific_energy`)

Registry evidence:

- `data/registries/quantity_registry.json`
- `data/registries/quantity_type_registry.json`
- `data/registries/dimension_registry.json`
- `data/registries/unit_registry.json`

## 2. Invariants, Conservation, and Tier Contracts

Constitution authority:

- `docs/physics/PHYSICS_CONSTITUTION.md`

Declared baseline:

- Mass conserved unless explicit transformation contract declares otherwise.
- Energy routed through explicit accounting (`quantity.energy_total`) with loss mapping to `quantity.heat_loss` or declared boundary flux exception.
- Momentum conservation scoped by tier applicability and external field forces.
- Entropy tracked diagnostically, not globally hard-failed.

Tier contracts:

- Macro: conservation/accounting without micro-force integration.
- Meso: network + constitutive-model + field sampling substrate.
- Micro (ROI): force/impulse integration only under budgeted deterministic contracts.

## 3. Exception / Magic Policy Baseline

Added profile + exception schemas:

- `schema/physics/physics_profile.schema`
- `schema/physics/exception_event.schema`
- `schemas/physics_profile.schema.json`
- `schemas/exception_event.schema.json`

Added policy registries:

- `data/registries/physics_profile_registry.json`
- `data/registries/loss_to_heat_policy_registry.json`

Baseline profiles:

- `phys.realistic.default`
- `phys.realistic.rank_strict`
- `phys.fantasy.permissive`
- `phys.lab.exotic`

Exception logging contract:

- No silent violations.
- `exception_event` must carry deterministic fingerprint + affected quantity deltas.
- proof/replay hooks documented in `docs/physics/PHYSICS_PROOF_REPLAY_HOOKS.md`.

## 4. Enforcement Readiness (PHYS-1 Precondition)

RepoX scaffolding wired:

- `INV-CROSS-DOMAIN-MUTATION-MUST-BE-MODEL`
- `INV-LOSS-MAPPED-TO-HEAT`
- `INV-UNREGISTERED-QUANTITY-FORBIDDEN`
- `INV-PHYS-PROFILE-DECLARED`

AuditX scaffolding added:

- `E205_ENERGY_BYPASS_SMELL`
- `E206_MOMENTUM_BYPASS_SMELL`
- `E207_MAGIC_SILENT_VIOLATION_SMELL`

Grammar and RWAM alignment:

- Motion/force transmission mapped to PHYS in RWAM.
- Action grammar updated for force/impulse/energy injection.
- Info grammar + artifact family updated so `exception_event` is `RECORD`.

## 5. Contract / Schema Impact

Changed:

- Added PHYS schema family (`physics_profile`, `exception_event`) and CompatX version registry entries.
- SessionSpec contract now requires top-level `physics_profile_id`.
- Quantity/dimension/unit registries expanded for PHYS canonical set.

Unchanged:

- No new solver implementation.
- No wall-clock coupling introduced.
- No intentional gameplay semantic change introduced by PHYS-0 artifacts.

## 6. Validation and Gate Outcomes

Validation level executed: STRICT + targeted FAST/STRICT subsets.

### 6.1 RepoX STRICT

- Command: `python tools/xstack/repox/check.py --repo-root . --profile STRICT`
- Result: PASS
- Message: `repox scan passed (files=1444, findings=17)` (warnings only)

### 6.2 AuditX STRICT

- Command: `python tools/xstack/auditx/check.py --repo-root . --profile STRICT`
- Result: FAIL
- Message: `auditx scan complete (changed_only=false, findings=2112, promoted_blockers=7)`
- Promoted blockers: `E179_INLINE_RESPONSE_CURVE_SMELL` in existing core files:
  - `src/fields/field_engine.py`
  - `src/mechanics/structural_graph_engine.py`
  - `src/mobility/maintenance/wear_engine.py`
  - `src/mobility/micro/constrained_motion_solver.py`
  - `src/mobility/traffic/traffic_engine.py`
  - `src/mobility/travel/travel_engine.py`
  - `src/signals/trust/trust_engine.py`

### 6.3 TestX STRICT (full)

- Command: `python tools/xstack/testx/runner.py --repo-root . --profile STRICT --cache off`
- Result: FAIL
- Summary: large existing branch drift; many failures rooted in `create_session_spec refused` and compile/runtime breakages outside PHYS-0 baseline.

### 6.4 Strict Build

- Command: `python tools/xstack/run.py --repo-root . --cache off strict`
- Result: REFUSAL
- Critical refusal cause:
  - `REFUSE_BUNDLE_COMPILE_FAILED` in session boot smoke and packaging validation.
  - Fresh compile probe (`use_cache=False`) refused with `invalid_port_type` in `data/registries/port_type_registry.json` (`payload_kind` values `fluid_stub` / `thermal` outside current enum).

### 6.5 Targeted PHYS TestX Subset

- Command:
  - `python tools/xstack/testx/runner.py --repo-root . --profile STRICT --cache off --subset test_repox_structural_integrity_invariants_registered,test_rw_matrix_schema_valid,testx.physics.profiles_registry_valid,testx.physics.quantities_have_dimensions,testx.physics.loss_to_heat_policy_present,testx.physics.exception_event_schema_valid,testx.physics.sessions_require_profile`
- Result: PASS (`selected_tests=7`)

## 7. Topology / Regression Baseline

Topology regenerated:

- `docs/audit/TOPOLOGY_MAP.json`
- `docs/audit/TOPOLOGY_MAP.md`

Current map fingerprint:

- `924a53b654b75b32335757fc638ff7d53a487535000e4df429d4040036426251`

## 8. Readiness Statement for PHYS-1

PHYS-0 constitution artifacts are established (docs, schemas, registries, invariants, grammar/RWAM/proof hooks, targeted tests).  
Global strict readiness remains blocked by pre-existing branch-level gate failures unrelated to PHYS-0 structural artifacts (AuditX promoted E179 set + compile/session boot refusals).
