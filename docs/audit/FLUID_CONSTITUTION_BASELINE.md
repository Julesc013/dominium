Status: DERIVED
Last Reviewed: 2026-03-16
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: DOC-CONVERGENCE
Replacement Target: canon-aligned documentation set for convergence and release preparation

# Fluid Constitution Baseline

Status: BASELINE
Last Updated: 2026-03-04
Scope: FLUID-0 constitutional baseline for infrastructure-scale liquid/gas flow.

## 1) Quantities and Tier Rules

Canonical FLUID substrate declarations:

- `quantity.mass_flow` (`dim.mass_flow`, `kg/s` policy)
- `quantity.pressure_head` (`dim.pressure` proxy)
- `bundle.fluid_basic = {quantity.mass_flow, quantity.pressure_head}`

Tier contract frozen:

- `F0`: bookkeeping-only mass transfer, no pressure solve
- `F1`: deterministic network pressure/head proxy mode
- `F2`: reserved (future ROI CFD; not implemented)

## 2) Safety Requirements

FLUID protection is SAFETY-pattern mediated, with required coverage for:

- pressure relief
- burst disk
- fail-safe shutdown
- LOTO-compatible isolation workflows

RepoX scaffolding added for FLUID safety discipline:

- `INV-FLUID-SAFETY-THROUGH-PATTERNS`
- `INV-NO-ADHOC-PRESSURE-LOGIC`

AuditX analyzers added:

- `E219 InlinePressureSmell`
- `E220 AdHocValveSmell`

## 3) Coupling Contracts

META-CONTRACT entries for FLUID are present and explicit:

- `FLUID -> THERM` via `model.fluid_heat_exchanger_stub`
- `FLUID -> INT` via `model.fluid_leak_flood_stub`
- `FLUID -> MECH` via `model.fluid_pressure_load_stub`

Explain contracts added:

- `fluid.leak`
- `fluid.overpressure`
- `fluid.cavitation`
- `fluid.burst`

## 4) Registry and Schema Baseline

FLUID schema and registry skeletons are integrated (strict v1.0.0):

- `schema/fluid/fluid_profile.schema`
- `schema/fluid/fluid_network_policy.schema`
- `schemas/fluid_profile.schema.json`
- `schemas/fluid_network_policy.schema.json`
- `data/registries/fluid_profile_registry.json`
- `data/registries/fluid_network_policy_registry.json`
- `data/registries/fluid_model_registry.json`

Null-boot policy coverage is present through `fluid.policy.none` and optional-runtime flags.

## 5) Governance and Determinism Notes

Relevant constitutional constraints upheld:

- process-only mutation (A2)
- deterministic ordering/replay obligations (A1/E2/E6)
- pack-driven optionality and explicit degrade/refusal paths (A9/A10/A11)

Topology map regenerated:

- `docs/audit/TOPOLOGY_MAP.json`
- `docs/audit/TOPOLOGY_MAP.md`

## 6) Gate Execution

Executed on 2026-03-04:

- RepoX STRICT: `pass` (warnings only)
- AuditX STRICT: `fail` (global promoted blockers)
- TestX STRICT full-profile: `fail` (pre-existing suite failures outside FLUID scope)
- TestX FLUID subset: `pass`
  - `test_fluid_profiles_registry_valid`
  - `test_fluid_null_boot_ok`
  - `test_fluid_contracts_present`
- strict build (`tools/xstack/run.py strict --cache on`): `refusal`
  - blocked by pre-existing `compatx/session_boot/packaging` refusals and global AuditX/TestX failures

AuditX promoted blockers observed are `E179_INLINE_RESPONSE_CURVE_SMELL` in non-FLUID files:

- `src/fields/field_engine.py:922`
- `src/mechanics/structural_graph_engine.py:550`
- `src/mobility/maintenance/wear_engine.py:165`
- `src/mobility/micro/constrained_motion_solver.py:309`
- `src/mobility/traffic/traffic_engine.py:125`
- `src/mobility/travel/travel_engine.py:621`
- `src/signals/trust/trust_engine.py:346`

## 7) Readiness Checklist for FLUID-1

Ready:

- constitutional quantities/bundle frozen
- tier/coupling/explain contracts declared
- safety doctrine and enforcement scaffolding present
- schema/registry baseline in place
- null-boot contract validated (targeted)

Blocked before claiming global STRICT green:

- existing cross-domain AuditX promoted blockers
- existing global TestX STRICT failures not introduced by FLUID-0
- existing strict pipeline refusals (compatx/session_boot/packaging)
