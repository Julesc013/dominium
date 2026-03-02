# MICRO_CONSTRAINED_MOTION_BASELINE

Status: BASELINE
Last Updated: 2026-03-02
Scope: MOB-6 micro constrained motion in ROI with deterministic derailment/coupling/junction handoff.

## 1) Solver Behavior

- Authoritative micro constrained solver process:
  - `process.mobility_micro_tick`
- Deterministic state update loop:
  - input rows are normalized and processed by sorted `vehicle_id`
  - kinematic integration uses integer math (`s_param`, `velocity`, `acceleration`)
  - speed cap and traction modifiers are applied via effect/field snapshots
- ROI gating is mandatory:
  - explicit `roi_vehicle_ids` required
  - non-ROI/global micro simulation is refused
- Budget behavior:
  - bounded `max_vehicle_updates_per_tick`
  - deterministic deferral ordering
  - deterministic downgrade to meso with fidelity decision-log entries

## 2) Derailment Model

- Deterministic threshold model:
  - `lateral_accel_units = v^2 / radius`
  - compare against threshold derived from base + track wear + friction + maintenance modifiers
- Process-only transition:
  - derailment state mutation routes through `process.mob_derail`
  - coupling constraints connected to the derailed vehicle are disabled
  - travel incident event + vehicle event are emitted deterministically
- Optional stochastic policy:
  - enabled only by derailment policy (`allow_stochastic=true`)
  - named stream required (`rng_stream_name`)
  - deterministic roll seed uses `H(rng_stream_name, vehicle_id, geometry_id, tick)`

## 3) Coupling Model

- Coupling process:
  - `process.coupler_attach`
- Validation:
  - vehicle ids must exist
  - optional mount point ids must resolve and pass mount compatibility
  - coupling type must be registry-declared
- Consist propagation:
  - active couplings are applied in deterministic order
  - lead (`vehicle_a_id`) drives trailing (`vehicle_b_id`) `s_param` by fixed offset
  - deferred/derailed vehicles are excluded from coupling propagation in the same tick

## 4) Junction/Switch Behavior

- Endpoint block behavior:
  - if endpoint reached, solver resolves next geometry through switch state + itinerary hint + deterministic tie-break
- Successful handoff:
  - vehicle transitions to next geometry at deterministic entry (`s_param=0`)
- No valid handoff:
  - vehicle is stopped and `event.blocked` incident_stub is emitted

## 5) EB Collision Integration

- Post-derail transition creates/updates deterministic vehicle body reference:
  - body id is stable (`body.vehicle.<hash>`)
  - motion micro state flips from guide-constrained to free body reference
- Collision participation is delegated to EB collision substrate for post-derail motion.

## 6) Integration Points (MOB-7 / MOB-8)

- MOB-7 free motion:
  - derailed vehicle body references are already emitted for handoff into free-motion micro solver
- MOB-8 signals/interlocking:
  - current switch/junction candidate resolution can be replaced with signal interlocking constraints without changing micro state schemas
- Reenactment:
  - incident/travel event payloads include speed/radius/wear/friction context for deterministic replay reconstruction

## 7) Performance Guarantees

- No global micro body simulation introduced.
- ROI-only solver execution with deterministic budget degradation.
- Deterministic ordering invariants:
  - vehicle update ordering by `vehicle_id`
  - coupling application ordering by `(vehicle_a_id, vehicle_b_id, constraint_id)`
  - normalized row persistence for stable replay hashes

## 8) Gate Runs (2026-03-02)

- RepoX:
  - command: `python tools/xstack/repox/check.py --repo-root . --profile STRICT`
  - status: `pass` (warnings only)
- AuditX:
  - command: `python tools/xstack/auditx/check.py --repo-root . --profile STRICT`
  - status: `pass` (scan executed; warnings reported)
- TestX (MOB-6 subset):
  - command: `python tools/xstack/testx/runner.py --repo-root . --profile STRICT --cache off --subset testx.mobility.micro_solver_deterministic,testx.mobility.derailment_threshold_trigger,testx.mobility.speed_cap_effect_applied,testx.mobility.coupling_consist_order_deterministic,testx.mobility.junction_switch_state_handoff,testx.mobility.budget_downgrade_to_meso_logged`
  - status: `pass` (6/6)
- strict build:
  - command: `python tools/setup/build.py --repo-root . --bundle bundle.base.lab --out build/dist.strict.mob6 --cache on --format json`
  - status: `complete` (`result=complete`)
- topology map update:
  - command: `python tools/governance/tool_topology_generate.py --repo-root . --out-json docs/audit/TOPOLOGY_MAP.json --out-md docs/audit/TOPOLOGY_MAP.md`
  - status: `complete` (`node_count=2416`, `edge_count=107501`)
  - deterministic fingerprint: `3b295646b4f31e8245f2e2f69ff29567ca061494ab3f33f9c2cfd5eb7de134dc`
