Status: DERIVED
Last Reviewed: 2026-03-02
Supersedes: none
Superseded By: none
Version: 1.0.0
Scope: MOB-1 GuideGeometry baseline and readiness handoff.
Stability: provisional
Future Series: DOC-CONVERGENCE
Replacement Target: canon-aligned documentation set for convergence and release preparation

# GuideGeometry Baseline

## Constitutional Coverage
- Process-only mutation is preserved for GuideGeometry lifecycle through:
  - `process.geometry_create`
  - `process.geometry_edit`
  - `process.geometry_finalize`
  - `process.formalization_accept_candidate`
- Deterministic behavior is preserved through canonical ordering, deterministic IDs, and deterministic snap/metric derivation.
- Inference remains derived-only until accepted through formalization control/process paths.

## Schemas and Registries
- Schemas added (strict `1.0.0`):
  - `schema/mobility/guide_geometry.schema`
  - `schema/mobility/geometry_type.schema`
  - `schema/mobility/junction.schema`
  - `schema/mobility/geometry_candidate.schema`
- Registries added:
  - `data/registries/geometry_type_registry.json`
  - `data/registries/junction_type_registry.json`
  - `data/registries/geometry_snap_policy_registry.json`
- Registry compile/lockfile path validated after integration:
  - `python tools/xstack/registry_compile/registry_compile.py --repo-root .`
  - result: `complete`

## Spec Integration
- `process.spec_apply_to_target` supports attaching `spec_id` to `target_kind=geometry`.
- `process.spec_check_compliance` integrates geometry-derived metrics:
  - curvature radius summaries
  - gauge width summary/stub check
  - clearance envelope summary/stub path
- Noncompliance surfaces remain explicit via deterministic compliance results/refusal pathways.
- Curvature-speed mismatch can emit `effect.speed_cap` on geometry segments for downstream mobility policies.

## Formalization Integration
- `process.formalization_accept_candidate` now materializes canonical GuideGeometry artifacts on acceptance.
- Deterministic geometry identity uses formalization/candidate/spec/tick bucket inputs.
- Accepted artifacts are linked back through:
  - `formalization_states.formal_artifact_ref`
  - `geometry_candidates` rows
- `process.formalization_promote_networked` remains deferred for MOB-2.

## UX Overlays and Planning Flow
- Planning path:
  - plan intents carry ghost previews in plan artifact spatial preview payloads
  - execution path emits guide geometry creation commitments/processes
- Diegetic raw path remains valid without immediate formal guide geometry.
- RND inspection/overlay integration includes:
  - centerline/wireframe renderables for geometry scopes
  - junction overlay support
  - deterministic overlay metadata/hashes
- Interaction affordances added:
  - `interaction.draw_guide`
  - `interaction.snap_endpoint`
  - `interaction.attach_spec`
  - `interaction.validate_spec`
  - `interaction.accept_inferred_candidate`

## Extension Points (MOB-2 and MOB-6)
- MOB-2 network integration:
  - junction connectivity/state machine references are in place for network graph promotion
  - geometry/junction IDs are stable for graph node/edge binding
  - no routing/signaling solver semantics are hardcoded in MOB-1
- MOB-6 micro solver integration:
  - GuideGeometry exposes deterministic parameterization and cached derived metrics for micro kinematic consumers
  - budget degradation outputs and decision-log entries provide deterministic fidelity arbitration hooks
  - field/spec/effect coupling surfaces are available without introducing physics-side nondeterminism

## Enforcement and Quality
- RepoX invariants in scope:
  - `INV-GEOMETRY-CREATION-PROCESS-ONLY`
  - `INV-NO-HARDCODED-GAUGE`
- AuditX analyzers in scope:
  - `E145_GEOMETRY_MUTATION_BYPASS_SMELL`
  - `E146_HARDCODED_TRACK_SPEC_SMELL`
- Targeted MOB-1 TestX coverage includes:
  - `testx.mobility.geometry_create_deterministic`
  - `testx.mobility.snap_policy_deterministic`
  - `testx.mobility.spec_compliance_check_deterministic`
  - `testx.mobility.formalization_accept_creates_geometry`
  - `testx.mobility.guide_geometry.render_overlay_hash_stable`
  - `testx.mobility.budget_degrade_geometry_metrics`

## Gate Snapshot (2026-03-02)
- RepoX:
  - command: `python tools/xstack/repox/check.py --repo-root . --profile FAST`
  - status: `pass` (warn findings present)
- AuditX:
  - command: `python tools/xstack/auditx/check.py --repo-root . --profile FAST`
  - status: `pass` (warn findings present)
- TestX:
  - command: `python tools/xstack/testx/runner.py --repo-root . --profile STRICT --subset testx.mobility.geometry_create_deterministic,testx.mobility.snap_policy_deterministic,testx.mobility.spec_compliance_check_deterministic,testx.mobility.formalization_accept_creates_geometry,testx.mobility.guide_geometry.render_overlay_hash_stable,testx.mobility.budget_degrade_geometry_metrics`
  - status: `pass` (`selected_tests=6`)
- Strict build:
  - command: `python tools/setup/build.py --repo-root . --bundle bundle.base.lab --out build/dist.strict.mob1 --cache on --format json`
  - result: `complete`
- Topology map update:
  - command: `python tools/governance/tool_topology_generate.py --repo-root . --out-json docs/audit/TOPOLOGY_MAP.json --out-md docs/audit/TOPOLOGY_MAP.md`
  - result: `complete`
  - deterministic fingerprint: `120fc8744c62c24c24b20d0da267dbe823a1a2c1fc73fd501bf76f9d1d859420`
