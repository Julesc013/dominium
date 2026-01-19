# Phase 2–5 Fixlist (Docs + Enforcement Only)

This list captures required clarifications and missing enforcement hooks.  
No gameplay redesigns are included.

## A) Required doc clarifications (blocking)

1) Align dependency/ownership headers with Phase-1 law across Phase 2–5 specs.
   - Update remaining specs that still state `engine -> libs/schema` or allow launcher/setup to use engine.
   - Targets include: `docs/SPEC_EFFECT_FIELDS.md`, `docs/SPEC_SENSORS.md`, `docs/SPEC_COMMUNICATION.md`,
     `docs/SPEC_COMMAND_MODEL.md`, `docs/SPEC_DOCTRINE_AUTONOMY.md`, `docs/SPEC_FIDELITY_PROJECTION.md`,
     `docs/SPEC_PROVENANCE.md`, `docs/SPEC_EVENT_DRIVEN_STEPPING.md`, `docs/SPEC_FIDELITY_DEGRADATION.md`,
     `docs/SPEC_TIME_CORE.md`, `docs/SPEC_TIME_FRAMES.md`, `docs/SPEC_TIME_STANDARDS.md`,
     `docs/SPEC_CALENDARS.md`, `docs/SPEC_SCHEDULING.md`, `docs/SPEC_TIME_KNOWLEDGE.md`,
     `docs/SPEC_UI_CAPABILITIES.md`, `docs/SPEC_UI_WIDGETS.md`, `docs/SPEC_UI_PROJECTIONS.md`,
     `docs/SPEC_MARKETS.md`, `docs/SPEC_MONEY_STANDARDS.md`, `docs/SPEC_PROPERTY_RIGHTS.md`,
     `docs/SPEC_FACTIONS.md`, `docs/SPEC_KNOWLEDGE_VIS_COMMS.md`.

2) Resolve legacy spec conflicts.
   - Deprecate or reconcile `docs/SPEC_KNOWLEDGE.md` with `docs/SPEC_INFORMATION_MODEL.md` and
     `docs/SPEC_KNOWLEDGE_VIS_COMMS.md`.
   - Ensure any `dknowledge_*` references are explicitly game-layer derived caches, not engine APIs.

3) Require schema governance for all data-defined structures.
   - Add schema/versioning notes (DATA0) to: standards, WSS providers, effect fields, sensors,
     comm channels, command intents, doctrine rules, interest sets, fidelity policy, UI widgets/layouts,
     money standards, market definitions, property rights, faction data.

## B) Determinism & scheduling clarifications (high)

4) Add explicit fixed-point/rational constraints where “scalar” or “physical computation” appears.
   - `docs/SPEC_TIME_WARP.md` (sim_rate), `docs/SPEC_SCHEDULING.md` (astronomical recurrence),
     `docs/SPEC_EFFECT_FIELDS.md` (evaluation math).

5) Require `next_due_tick` exposure for all macro subsystems in Phase 2–5.
   - Belief decay (`docs/SPEC_INFORMATION_MODEL.md`), doctrine review (`docs/SPEC_DOCTRINE_AUTONOMY.md`),
     market clearing (`docs/SPEC_MARKETS.md`), faction scheduling (`docs/SPEC_FACTIONS.md`), comm delivery
     (`docs/SPEC_COMMUNICATION.md`), sensor cadence (`docs/SPEC_SENSORS.md`).

6) Clarify UI/camera interest rules.
   - In `docs/SPEC_INTEREST_SETS.md`, ensure UI/camera focus cannot directly activate micro simulation
     or bypass authoritative gating.

## C) Missing enforcement hooks (high)

7) CI wiring for static checks that Phase 2–5 rely on.
   - Add `tools/ci/arch_checks.py` to CI or CTest.
   - Wire determinism gate suites (DET-G1..G6).
   - Add render canon checks (REND-*).

8) Add CI checks for schema presence and versioning in Phase 2–5 data packs.
   - Extend DATA1 validation to cover standards, WSS providers, UI widgets/layouts, markets, and factions.

9) Add event-driven scheduling lint for macro subsystems.
   - Enforce `next_due_tick` usage and ban global scans in Phase 2–5 modules.

## D) Low-risk doc clarifications (medium)

10) Clarify “real continuous time” wording in `docs/SPEC_TIME_CORE.md` to explicitly mean fixed-point ACT.
11) Clarify that market quotes are InfoRecords and must pass epistemic gating in `docs/SPEC_MARKETS.md`.
12) Clarify that WSS LOD policy is game-owned; engine provides only deterministic helpers in
    `docs/SPEC_WORLD_SOURCE_STACK.md` (partially addressed).
