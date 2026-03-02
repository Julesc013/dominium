# MOB11 Retro-Consistency Audit

Date: 2026-03-03
Scope: Mobility determinism envelope hardening (MOB-1..10 integration validation).

## Audit Targets

- Direct position mutation bypassing mobility solvers.
- Local downgrade logic outside deterministic negotiation/runtime policy.
- Incident logging coverage through process/event pathways.
- Silent teleports and silent delays.

## Findings

### 1) Direct Position Mutation Bypass

- No new bypass path found for authoritative mobility movement.
- Constrained micro updates flow through `process.mobility_micro_tick` in [tools/xstack/sessionx/process_runtime.py](../../tools/xstack/sessionx/process_runtime.py), which calls `step_micro_motion` from [src/mobility/micro/constrained_motion_solver.py](../../src/mobility/micro/constrained_motion_solver.py).
- Free micro updates flow through `process.mobility_free_tick` in [tools/xstack/sessionx/process_runtime.py](../../tools/xstack/sessionx/process_runtime.py), which calls `step_free_motion` from [src/mobility/micro/free_motion_solver.py](../../src/mobility/micro/free_motion_solver.py).
- Derailment transitions are routed through `process.mob_derail` and `_apply_derailment_transition` in [tools/xstack/sessionx/process_runtime.py](../../tools/xstack/sessionx/process_runtime.py); no direct off-process derail mutation path found.

### 2) Downgrade Logic Placement

- Mobility budget degradation is deterministic and process-visible:
  - `process.travel_tick` deferred vehicle ordering and degradation metadata.
  - `process.mobility_micro_tick` deferred ordering + optional deterministic collapse to meso.
  - `process.mobility_free_tick` ROI/budget deferral and optional meso downgrade.
- Downgrade reasoning is carried in decision/fidelity rows with stable reason codes (for example `degrade.mob.micro_budget`, `degrade.mob.travel_tick_budget`) in [tools/xstack/sessionx/process_runtime.py](../../tools/xstack/sessionx/process_runtime.py).
- No hidden wall-clock or random downgrade branch found in these paths.

### 3) Incident Logging Coverage

- Mobility incidents are represented in `travel_events` via deterministic `build_travel_event(... kind="incident_stub")` and explicit reason codes:
  - derailment, collision, visibility, wind, breakdown, wear-related failures.
- Signal/switch and blockage outcomes are also emitted as deterministic travel or mobility event rows.
- Process-triggered incident pathways observed in:
  - `process.mob_derail`
  - `process.mobility_micro_tick`
  - `process.mobility_free_tick`
  - wear/failure handlers in [tools/xstack/sessionx/process_runtime.py](../../tools/xstack/sessionx/process_runtime.py).

### 4) Silent Teleport / Silent Delay Check

- Delay emission is explicit through `travel_event.kind="delay"` and `details.reason="event.delay.congestion"` from macro travel tick logic.
- No silent congestion delay update path found in [src/mobility/travel/travel_engine.py](../../src/mobility/travel/travel_engine.py) and process integration.
- Non-mobility camera teleport exists (`process.camera_teleport`) but is explicit process-driven and not a mobility vehicle mutation pathway.

## Risks / Gaps

- Mobility reenactment/proof coverage is currently split across travel events, fidelity logs, and control proof bundles; no single mobility reenactment descriptor contract exists yet.
- Cross-tier transition continuity checks exist in multiple tests but are not consolidated into a dedicated mobility envelope validation set.

## Migration / Hardening Plan (MOB11)

1. Introduce a mobility reenactment descriptor schema + deterministic descriptor builder.
2. Add explicit cross-tier continuity validation tests (macro/meso/micro and ROI entry/exit collapse behavior).
3. Add mobility stress and determinism compare tools for envelope assertions.
4. Extend control proof bundles with mobility hashes (event/congestion/signal/derailment).
5. Add mobility regression lock baseline with explicit update tag requirement.
6. Publish extension contract and final baseline report.
