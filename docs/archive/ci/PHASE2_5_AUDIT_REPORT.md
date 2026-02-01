Status: HISTORICAL
Last Reviewed: 2026-02-01
Supersedes: none
Superseded By: docs/architecture/CANON_INDEX.md

This document is archived.
Reason: Superseded by docs/architecture/CANON_INDEX.md.
Do not use for implementation.

This document is archived.
Reason: Superseded by docs/architecture/CANON_INDEX.md.
Do not use for implementation.

This document is archived.
Reason: Superseded by unknown.
Do not use for implementation.

# ARCHIVED: Phase 2–5 Audit Report (PH2_5-AUDIT)





Archived: point-in-time audit.


Reason: Historical enforcement snapshot; current status is tracked elsewhere.


Superseded by:


- `docs/ci/CI_ENFORCEMENT_MATRIX.md`


- `docs/ci/EXECUTION_ENFORCEMENT_CHECKS.md`


- `docs/architecture/INVARIANTS.md`


Still useful: background on Phase 2–5 gaps.





# Phase 2–5 Audit Report (PH2_5-AUDIT)





Status: NEEDS FIX (blockers present)


Scope: Phase 2 (STD0, WSS0, EF0, INF0–INF2, CMD0–CMD1, FP0–FP3), Phase 3 (T0–T4, TW0–TW1), Phase 4 (UI0–UI3), Phase 5 (E0–E4)





## Global findings (cross-phase)


- Dependency/ownership headers in many Phase 2–5 specs conflict with Phase-1 law (engine -> nothing; game -> engine only; launcher/setup -> libs+schema only). This is a systemic doc inconsistency.


- Most Phase 2–5 specs define data-driven structures but declare `SCHEMA: None`, violating DATA0 governance.


- Several systems define cadence/decay but do not mandate `next_due_tick` exposure or event-driven scheduling.


- Legacy specs (`docs/specs/SPEC_KNOWLEDGE.md`, `docs/specs/SPEC_ECONOMY.md`) conflict with newer Phase 2–5 models and Phase-1 enforcement.





## Phase 2 — Core substrate & world semantics





Covered docs: `docs/specs/SPEC_STANDARDS_AND_RENDERERS.md`, `docs/specs/SPEC_WORLD_SOURCE_STACK.md`, `docs/specs/SPEC_EFFECT_FIELDS.md`, `docs/specs/SPEC_INFORMATION_MODEL.md`, `docs/specs/SPEC_SENSORS.md`, `docs/specs/SPEC_COMMUNICATION.md`, `docs/specs/SPEC_COMMAND_MODEL.md`, `docs/specs/SPEC_DOCTRINE_AUTONOMY.md`, `docs/specs/SPEC_FIDELITY_PROJECTION.md`, `docs/specs/SPEC_PROVENANCE.md`, `docs/specs/SPEC_EVENT_DRIVEN_STEPPING.md`, `docs/specs/SPEC_FIDELITY_DEGRADATION.md`, `docs/specs/SPEC_INTEREST_SETS.md`, `docs/specs/SPEC_KNOWLEDGE.md`, `docs/specs/SPEC_KNOWLEDGE_VIS_COMMS.md`.





| Dimension | Status | Notes |


| --- | --- | --- |


| A) Engine/Game boundary | NEEDS FIX | Many specs still claim engine can depend on schema/libs; WSS previously implied engine-managed interest; legacy knowledge/economy specs imply engine ownership. |


| B) Determinism & replay | NEEDS FIX | Determinism is stated but some specs lack explicit fixed-point-only constraints for all evaluation paths (effect fields, belief decay). |


| C) Event-driven & scalability | NEEDS FIX | Sensors/comms are event-driven, but belief decay and doctrine reviews do not universally require `next_due_tick` exposure. |


| D) Epistemic & UI safety | NEEDS FIX | Info/command/market specs require epistemic gating, but Interest Sets allow UI/camera focus without explicit anti-bypass constraints. |


| E) Schema & data governance | BLOCKER | Standards, WSS providers, sensors, commands, doctrine, interest sets, and effect fields are data-defined but lack schema/versioning references. |


| F) Cross-system interactions | NEEDS FIX | WSS x Provenance and Effect Fields x Info are described, but enforcement is not defined. |


| G) LIFE/CIV readiness | NEEDS FIX | Provenance, fidelity, and event-driven stepping are good foundations, but schema gaps and legacy knowledge spec are blockers for LIFE/CIV. |





Key findings:


- `docs/specs/SPEC_KNOWLEDGE.md` conflicts with `docs/specs/SPEC_INFORMATION_MODEL.md` and provides engine-flavored APIs; this is a blocker for epistemic correctness and engine/game separation.


- `docs/specs/SPEC_WORLD_SOURCE_STACK.md` required clarification that game owns interest policy; engine only provides deterministic helpers.


- `docs/specs/SPEC_INTEREST_SETS.md` requires explicit constraint that UI/camera focus cannot directly activate authoritative micro simulation.





## Phase 3 — Time system





Covered docs: `docs/specs/SPEC_TIME_CORE.md`, `docs/specs/SPEC_TIME_FRAMES.md`, `docs/specs/SPEC_TIME_STANDARDS.md`, `docs/specs/SPEC_CALENDARS.md`, `docs/specs/SPEC_SCHEDULING.md`, `docs/specs/SPEC_TIME_WARP.md`, `docs/specs/SPEC_TIME_KNOWLEDGE.md`.





| Dimension | Status | Notes |


| --- | --- | --- |


| A) Engine/Game boundary | NEEDS FIX | Time specs still carry Phase-1-incompatible dependency blocks. |


| B) Determinism & replay | NEEDS FIX | Time warp and astronomical recurrence require explicit fixed-point constraints. |


| C) Event-driven & scalability | NEEDS FIX | Scheduling/recurrence does not mandate `next_due_tick` exposure or bounded expansion. |


| D) Epistemic & UI safety | PASS | Time knowledge gating uses devices and uncertainty; no truth leak assumptions. |


| E) Schema & data governance | NEEDS FIX | Time standards, calendars, and recurrence rules are data-defined but lack schema/versioning references. |


| F) Cross-system interactions | NEEDS FIX | Time × economy and time × info rules are stated but enforcement/CI hooks are missing. |


| G) LIFE/CIV readiness | NEEDS FIX | Time is compatible with LIFE/CIV once schemas and deterministic scheduling are formalized. |





Key findings:


- `docs/specs/SPEC_TIME_WARP.md` must require deterministic fixed-point/rational sim_rate and explicit logging of warp changes for replay/lockstep.


- `docs/specs/SPEC_SCHEDULING.md` must clarify deterministic astronomical calculations and avoid float usage.





## Phase 4 — UI & Epistemic Interface





Covered docs: `docs/specs/SPEC_EPISTEMIC_INTERFACE.md`, `docs/specs/SPEC_UI_CAPABILITIES.md`, `docs/specs/SPEC_UI_WIDGETS.md`, `docs/specs/SPEC_UI_PROJECTIONS.md`.





| Dimension | Status | Notes |


| --- | --- | --- |


| A) Engine/Game boundary | NEEDS FIX | Ownership headers conflict with Phase-1 dependency rules (tools/schema references). |


| B) Determinism & replay | PASS | Capability snapshots specify deterministic ordering and replay equivalence. |


| C) Event-driven & scalability | NEEDS FIX | Capability derivation cost is bounded but interest-set coupling is not explicit. |


| D) Epistemic & UI safety | PASS | UI uses capability snapshots only; no authoritative reads. |


| E) Schema & data governance | NEEDS FIX | Widget/layout/config capability definitions require schema/versioning. |


| F) Cross-system interactions | PASS | UI projections explicitly consume capability snapshots only. |


| G) LIFE/CIV readiness | PASS | LIFE/CIV can safely expose UI via capability layer once schemas exist. |





Key findings:


- UI specs are epistemically correct but lack schema governance for widget/layout formats.


- Capability derivation should be explicitly bounded by interest sets to prevent global scans.





## Phase 5 — Economy & Governance





Covered docs: `docs/specs/SPEC_LEDGER.md`, `docs/specs/SPEC_MARKETS.md`, `docs/specs/SPEC_ECONOMY.md`, `docs/specs/SPEC_MONEY_STANDARDS.md`, `docs/specs/SPEC_PROPERTY_RIGHTS.md`, `docs/specs/SPEC_FACTIONS.md`.





| Dimension | Status | Notes |


| --- | --- | --- |


| A) Engine/Game boundary | NEEDS FIX | `docs/specs/SPEC_LEDGER.md` header conflicted with engine-owned ledger primitives; dependency blocks remain inconsistent. |


| B) Determinism & replay | NEEDS FIX | Ledger/markets are deterministic, but economy scaffolding implies global scans. |


| C) Event-driven & scalability | BLOCKER | `docs/specs/SPEC_ECONOMY.md` defines best-offer scans that violate no-global-iteration law. |


| D) Epistemic & UI safety | NEEDS FIX | Market quotes are InfoRecords, but economy scaffolding lacks epistemic gating. |


| E) Schema & data governance | BLOCKER | Assets, instruments, markets, property rights, and faction data lack schema/versioning references. |


| F) Cross-system interactions | NEEDS FIX | Economy × time and economy × info interactions are documented but not enforced. |


| G) LIFE/CIV readiness | NEEDS FIX | Ledger is a strong base, but economy scaffolding and schema gaps block LIFE/CIV. |





Key findings:


- `docs/specs/SPEC_ECONOMY.md` must explicitly forbid global scans and require event-driven/interest-bounded access.


- Asset and market definitions are data-driven and must be schema-governed per DATA0.





## Cross-system interaction safety (Phase 2–5)





| Interaction | Safe if | Breaks if | Enforcement |


| --- | --- | --- | --- |


| Time × Economy | Ledger events are scheduled in ACT and markets clear on due ticks. | Market clears use wall-clock or floats. | DET-TIME-001 + PERF-EVT-001/002 (missing CI wiring). |


| Economy × Info | Quotes are InfoRecords with latency/uncertainty. | UI reads ledger balances directly. | EPIS-* + UI-BYPASS-001 (partial). |


| Info × UI | Capability snapshots only; no authoritative reads. | UI queries world/ledger directly. | EPIS-CAP-003 + EPIS-BYPASS-001 (partial). |


| Fidelity × Rendering | Rendering consumes derived projections only. | Renderer writes to sim hashes. | REND-DET-001 (missing). |


| WSS × Provenance | WSS outputs are tagged by provider and hashed. | Derived WSS output fabricated without provenance. | SCALE-FID-001/002 (scan not CI-wired). |





## Conclusion





Phase 2–5 are not yet internally consistent with Phase-1 enforcement law. The most urgent blockers are:


- Schema governance missing across Phase 2–5 data-defined structures.


- Legacy economy and knowledge scaffolding contradict event-driven and epistemic laws.


- Phase-1 dependency law conflicts with many Phase 2–5 ownership headers.





These are documentation and enforcement gaps; no gameplay redesign is required.
