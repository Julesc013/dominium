Status: BASELINE
Last Reviewed: 2026-03-05
Supersedes: docs/system/MACROCAPSULE_BEHAVIOR_MODEL.md
Superseded By: none
Version: 1.0.0
Compatibility: SYS-3 system tier and ROI scheduling contract.

# System Tier and ROI Policy

## Purpose
Define deterministic, budgeted system-tier transitions (`micro`, `meso`, `macro`) with explicit process logging and invariant preservation.

## A) Tier Modes for Systems
- `tier.micro`: full internal assembly graph simulation active.
- `tier.meso`: reserved intermediate fidelity (optional future execution path).
- `tier.macro`: MacroCapsule active; internal graph collapsed.

All tier transitions are process-governed; no renderer/UI/tool direct mutation is allowed.

## B) Deterministic Degradation Order
- Degradation order is declared in each system tier contract via `deterministic_degradation_order`.
- Required directional policy:
  - degrade: `micro -> meso -> macro`
  - refine: `macro -> meso -> micro` only via explicit transition approval (including forced-expand pathways).
- Unsupported transitions are denied deterministically and logged.

## C) ROI Scheduling Policy
Per canonical tick (`process.system_roi_tick`):
1. Enumerate systems sorted by `system_id`.
2. Resolve desired tier:
   - ROI / inspection / hazard / fidelity request: prefer `micro`
   - outside ROI: prefer `macro`
3. Project desired tier onto contract-supported tiers.
4. Build transition requests (`expand`/`collapse`), ordered deterministically by:
   - priority class (`inspection`, `hazard`, `roi`, `background`)
   - `system_id` tie-break.

ROI inputs may include:
- player proximity/presence
- inspection tasks
- hazard proximity flags
- control-plane fidelity requests.

## D) Budget Arbitration via CTRL
- Each transition request carries:
  - `cost_model_id`
  - `priority_class`
  - transition kind and target tier
- Budget denials are deterministic and logged as decision records.
- Deterministic caps enforce bounded work per tick:
  - `max_expands_per_tick`
  - `max_collapses_per_tick`.

## E) Transition Guarantees
### Collapse
- Must validate:
  - interface signature
  - boundary invariants
  - collapse eligibility preconditions
    - no unresolved hazards
    - no pending internal events
    - no open scheduled internal tasks
    - no open branch dependencies

### Expand
- Must validate:
  - provenance anchor hash
  - interface signature still matches capsule snapshot
  - boundary invariants

Failures are explicit refusals; no silent tier mutation is permitted.

## F) Proof and Replay
- SYS-3 proof chains:
  - `system_tier_change_hash_chain`
  - `collapse_expand_event_hash_chain`
- Replay verifier:
  - `tools/system/tool_replay_tier_transitions`
- Tier change events are canonical RECORD-linked artifacts.

## Non-Goals
- No new physics/flow/thermal/chemical solvers.
- No wall-clock scheduling.
- No semantics changes to collapse/expand internals beyond safety prechecks and logging discipline.
