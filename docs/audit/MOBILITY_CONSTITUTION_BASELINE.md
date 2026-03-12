Status: DERIVED
Last Reviewed: 2026-03-02
Version: 1.0.0
Scope: MOB-0 Mobility Constitution baseline and readiness handoff.
Stability: provisional
Future Series: DOC-ARCHIVE
Replacement Target: legacy reference surface retained without current binding authority

# Mobility Constitution Baseline

## Constitutional Rules (Frozen)
- Mobility is tiered and deterministic:
  - macro = commitments/ETAs/schedules only
  - meso = occupancy/signals/timetables/congestion arbitration
  - micro = ROI-only kinematic and constraint simulation
- Movement semantics are constraint-class driven (`constrained_1D`, `constrained_2D`, `constrained_3D`, `orbital_path`, `field_following`, `free_motion`), not vehicle hardcoding.
- No mode flags: behavior composition remains profile/policy/spec driven.
- Process-only mutation remains mandatory; direct truth-position mutation outside process execution is disallowed.
- Control plane is the only execution path for driving/dispatch/planning/scheduling intents.
- Mobility degradations/refusals must be explicit and logged; no silent speed/traction multipliers.
- Optional packs remain optional; missing content must degrade/refuse deterministically.

## Formalization Lifecycle States
- `RAW`: only physical assemblies/earthworks exist.
- `INFERRED`: candidate guide geometry is derived and inspectable.
- `FORMAL`: authored guide geometry + constraints + policy bindings exist.
- `NETWORKED`: connected movement graph with rules/signals/schedules exists.
- Promotions between states require explicit control intents and deterministic process commits.

## Integration Points
- SPEC-1:
  - movement infrastructure and vehicles remain SpecSheet-driven (`gauge`, `clearance`, `curvature`, `load rating`, `max speed policy refs`)
  - deterministic compliance checks and inspectable refusal surfaces are required
- FORM-1:
  - lifecycle progression is bound to formalization state (`RAW -> INFERRED -> FORMAL -> NETWORKED`)
  - no hidden auto-formalization
- MECH-1:
  - mobility consumes structural integrity, bridge/load-path capacity, and failure risk surfaces
  - movement incidents map to explicit incident reason codes
- FIELD-1:
  - mobility consumes traction/visibility/icing/wind modifiers from FieldLayer through explicit Effects
  - no ad-hoc weather math outside field/effect pathways
- CTRL:
  - all mobility control enters via ControlIntent/IR and remains authority/law/epistemic gated
  - control grant remains seat/pose/control-binding mediated
- MAT:
  - mobility infrastructure is materially authored and maintained through MAT construction/maintenance/inspection commitments
  - no spontaneous route/material state mutation

## MOB-0 Registry and Codebook Baseline
- Refusal codes added:
  - `refusal.mob.no_route`
  - `refusal.mob.spec_noncompliant`
  - `refusal.mob.control_not_granted`
  - `refusal.mob.fidelity_denied`
  - `refusal.mob.speed_cap_exceeded`
  - `refusal.mob.signal_violation`
  - `refusal.mob.coupling_incompatible`
  - `refusal.mob.cross_shard_motion_forbidden`
- Incident reason codes added:
  - `incident.derailment.curvature`
  - `incident.derailment.track_wear`
  - `incident.collision`
  - `incident.breakdown.engine`
  - `incident.visibility_low`
  - `incident.wind_exceeded`
- Registry skeletons added (ID + schema-ref only; no hardcoded semantics):
  - `data/registries/mobility_vehicle_class_registry.json`
  - `data/registries/mobility_constraint_type_registry.json`
  - `data/registries/mobility_signal_type_registry.json`
  - `data/registries/mobility_speed_policy_registry.json`

## Enforcement Scaffolding (Warn-Now)
- RepoX invariants:
  - `INV-NO-TRAIN-SPECIALCASE`
  - `INV-MOB-THROUGH-CONTROL`
  - `INV-NO-GLOBAL-MICRO-MOTION`
  - `INV-MOB-USES-GUIDEGEOMETRY`
  - `INV-MOB-USES-NETWORKGRAPH`
- AuditX analyzers:
  - `E142_MOBILITY_SPECIAL_CASE_SMELL`
  - `E143_DIRECT_POSITION_MUTATION_SMELL`
  - `E144_ADHOC_SPEED_LIMIT_SMELL`

## MOB-1 Readiness Checklist
- [x] Constitution frozen and published (`docs/mobility/MOBILITY_CONSTITUTION.md`).
- [x] Legacy mobility hotspots audited with migration plan (`docs/audit/MOB0_RETRO_AUDIT.md`).
- [x] Mobility refusal + incident reason code surface registered.
- [x] Mobility registry skeletons integrated through compile/lockfile/runtime loading path.
- [x] Enforcement scaffolding (RepoX/AuditX) added at warn-now severity.
- [x] Topology map regenerated with mobility registry/schema surfaces.
- [ ] MOB-1 solver implementation (routing/occupancy/micro motion) intentionally deferred.

## Gate Snapshot (2026-03-02)
- topology map update (`python tools/governance/tool_topology_generate.py --repo-root . --commit-hash \"\" --generated-tick 0`):
  - PASS
  - fingerprint `231ac2790459fa9e8f5c07186149c804d771a538de8fe2a19f410692c2cd9792`
- RepoX (`python tools/xstack/repox/check.py --repo-root . --profile FAST`):
  - PASS (`status: pass`, warn-only findings)
- AuditX (`python tools/auditx/auditx.py scan --repo-root .`):
  - run complete (`result: scan_complete`, `findings_count: 1083`)
- TestX doc/schema/topology subset (`python tools/xstack/testx/runner.py --repo-root . --profile FAST --subset test_topology_map_includes_all_registries,test_topology_map_includes_all_schemas,test_topology_map_deterministic`):
  - PASS (`status: pass`, `selected_tests: 3`)
- strict build (`python tools/setup/build.py --repo-root . --bundle bundle.base.lab --out build/dist.strict.mob0 --cache on --format json`):
  - PASS (`result: complete`)
