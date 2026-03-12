Status: DERIVED
Last Reviewed: unknown
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: DOC-CONVERGENCE
Replacement Target: canon-aligned documentation set for convergence and release preparation

# Thermal Constitution Baseline

Status: Baseline complete (THERM-0)  
Date: 2026-03-03

## Scope Summary

THERM-0 establishes constitutional governance and scaffolding for thermal simulation without introducing a new heavy runtime solver tier.

Heat is normalized across existing substrates:

- quantities (`quantity.thermal_energy`, `quantity.heat_flow`, `quantity.heat_loss`)
- field (`field.temperature`)
- flow channels and quantity bundles
- constitutive model declarations
- safety/hazard hooks

## Quantities And Tiering

Thermal quantities:

- `quantity.thermal_energy` (J)
- `quantity.heat_flow` (J/tick)
- `quantity.heat_loss` (J/tick)

Tier envelope:

- `T0` macro bookkeeping baseline (always available)
- `T1` meso thermal-network conduction policy layer
- `T2` micro ROI diffusion reserved for future THERM-1+

## Coupling Rules

Loss-to-heat mapping is now explicit and documented:

- preferred: `quantity.heat_loss` / `quantity.thermal.heat_loss_stub`
- fallback: `effect.temperature_increase_local`

Attribution and replay requirements are required for all dissipative outputs.

## Safety Hooks

THERM prep registers safety templates:

- `safety.overtemp_trip`
- `safety.thermal_runaway`

No bespoke thermal trip logic is introduced in THERM-0.

## RWAM / Grammar Integration

RWAM and grammar surfaces now include THERM mapping:

- RWAM `series_affordance_coverage` includes `THERM`
- Action grammar thermal templates:
  - `action.therm.insulate`
  - `action.therm.cool`
  - `action.therm.vent_heat`
  - `action.therm.measure_temperature`
- INFO grammar includes thermal OBSERVATION/RECORD/REPORT mapping

## Artifacts Added

Audit/docs:

- `docs/audit/THERM0_RETRO_AUDIT.md`
- `docs/thermal/THERMAL_CONSTITUTION.md`
- `docs/thermal/LOSS_TO_HEAT_CONVENTION.md`
- `docs/audit/THERMAL_CONSTITUTION_BASELINE.md`

Schema/text contracts:

- `schema/thermal/thermal_node_kind.schema`
- `schema/thermal/thermal_edge_kind.schema`
- `schema/thermal/thermal_policy.schema`

JSON schemas:

- `schemas/thermal_node_kind.schema.json`
- `schemas/thermal_edge_kind.schema.json`
- `schemas/thermal_policy.schema.json`

Registries:

- `data/registries/thermal_policy_registry.json`
- `data/registries/thermal_model_registry.json`
- `data/registries/thermal_node_kind_registry.json`
- `data/registries/thermal_edge_kind_registry.json`

Enforcement:

- RepoX invariant prep: `INV-LOSS-MAPPED-TO-HEAT` (warn-phase)
- RepoX optionality check: `INV-THERM-POLICIES-OPTIONAL`
- AuditX analyzer: `E195_HEAT_LOSS_BYPASS_SMELL`

TestX:

- `test_thermal_domain_null_boot_ok`
- `test_loss_to_heat_convention_doc_present`
- `test_action_grammar_entries_present_for_thermal_measure`

## Gate Results

Executed commands:

- RepoX STRICT
  - `python tools/xstack/repox/check.py --repo-root . --profile STRICT`
  - Result: **PASS** (`status=pass`, findings present as warnings only)

- AuditX scan
  - `python tools/auditx/auditx.py scan --repo-root . --format both`
  - Result: **COMPLETE** (`findings_count=1573`, reports refreshed in `docs/audit/auditx/`)

- TestX targeted THERM-0 + affected governance checks
  - `python tools/xstack/testx/runner.py --repo-root . --profile FAST --cache off --subset test_thermal_domain_null_boot_ok,test_loss_to_heat_convention_doc_present,test_action_grammar_entries_present_for_thermal_measure,test_all_affordances_declared,test_no_series_without_affordance_mapping,test_rw_matrix_schema_valid,test_action_template_validation,test_all_actions_have_family`
  - Result: **PASS** (`8/8`)

- Strict build gate
  - `python scripts/dev/gate.py strict --repo-root . --only-gate build_strict`
  - Result: **PASS** (exit code 0)

- Topology map update
  - `python tools/governance/tool_topology_generate.py --repo-root .`
  - Result: **PASS** (`deterministic_fingerprint=ca2eae7703bfcc940d4d64708a7667396ac04ba0880af49dadba148733613e86`)

## Readiness For THERM-1

- [x] Constitutional tier model locked (`T0/T1/T2`)
- [x] Cross-domain loss-to-heat convention documented and enforced (warn-phase)
- [x] Registry + schema scaffolding created for thermal policy/kinds/models
- [x] Safety hook templates prepared (`overtemp_trip`, `thermal_runaway`)
- [x] Null boot optional policy path declared (`therm.policy.none`)
- [ ] Thermal network conduction runtime execution (THERM-1)
- [ ] Micro ROI diffusion model (THERM-2+)
