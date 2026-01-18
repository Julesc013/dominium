--------------------------------
OWNERSHIP & RESPONSIBILITY
--------------------------------
ENGINE:
- primitives only (IDs, scheduling, ledger hooks)
GAME:
- conflict rules, policies, resolution
SCHEMA:
- formats, versions, migrations
TOOLS:
- future editors/inspectors only (no runtime behavior).
FORBIDDEN:
- No runtime logic in schema specs.
- No random resistance events.
- No occupation without logistics and legitimacy records.
DEPENDENCIES:
- Engine -> (no dependencies outside engine/).
- Game -> engine public API only.
- Schema -> none (formats only).
- Tools -> schema + engine/game public APIs only.
--------------------------------
# SPEC_OCCUPATION_AND_RESISTANCE - Occupation and Resistance (CIV5-WAR0)

Status: draft
Version: 1

## Purpose
Define deterministic occupation conditions and resistance events that integrate
with governance, logistics, and LIFE pipelines.

## OccupationCondition schema
Required fields:
- occupation_id
- occupier_authority_id
- occupied_jurisdiction_id
- enforcement_capacity (deterministic value)
- legitimacy_support (bounded, deterministic)
- logistics_dependency_id
- start_act
- next_due_tick (ACT)
- status (active, degrading, ended)
- provenance_ref

Rules:
- Occupation exists only while enforcement capacity applies in the domain.
- Occupation degrades deterministically when logistics or legitimacy are absent.
- Updates are event-driven; no per-tick decay.

## ResistanceEvent schema
Required fields:
- resistance_id
- occupation_id
- trigger_reason (legitimacy_below_threshold, logistics_failure, enforcement_gap)
- trigger_act
- resolution_act
- order_key (deterministic)
- outcome_refs (casualties, resource deltas, legitimacy deltas)
- provenance_ref

Rules:
- Resistance is scheduled when thresholds are crossed.
- Outcomes are deterministic and processed at resolution_act only.
- Casualties must be emitted via LIFE2 pipelines.

## Legitimacy and logistics coupling
- Illegitimate occupation accelerates degradation and resistance cadence.
- No supply or transport capacity increases resistance pressure.
- War exhaustion is modeled as scheduled legitimacy decay events.

## Epistemic constraints
- Occupation and resistance knowledge is gated by sensors and reports.
- UI must reflect uncertainty and delays.

## Integration points
- Governance: `schema/governance/SPEC_LEGITIMACY.md`,
  `schema/governance/SPEC_ENFORCEMENT.md`
- Logistics: `schema/civ/SPEC_LOGISTICS_FLOWS.md`
- LIFE pipelines: `schema/life/SPEC_DEATH_AND_ESTATE.md`
- Knowledge gating: `schema/knowledge/SPEC_SECRECY.md`,
  `docs/SPEC_EPISTEMIC_INTERFACE.md`

## Prohibitions
- No random resistance events.
- No hidden, per-tick attrition loops.
- No occupation without logistics support records.

## Test plan (spec-level)
Required scenarios:
- Deterministic engagement resolution.
- Batch vs step equivalence.
- Logistics starvation effects.
- Occupation legitimacy decay.
- Epistemic uncertainty correctness.
- No global iteration with many conflicts.
