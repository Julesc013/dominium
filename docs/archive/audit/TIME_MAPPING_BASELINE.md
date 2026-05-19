Status: DERIVED
Last Reviewed: 2026-03-16
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: DOC-CONVERGENCE
Replacement Target: canon-aligned documentation set for convergence and release preparation

# Time Mapping Baseline

Date: 2026-03-04
Scope: TEMP-1

## Implemented Baseline

## Mapping models

- `model.time.proper_default_stub`
  - Inputs: `canonical_tick`, `field.gravity_vector`, `velocity`
  - Output: deterministic proper-time increment/value
- `model.time.civil_calendar_stub`
  - Inputs: `canonical_tick`
  - Output: deterministic civil-time value
- `model.time.warp_session_stub`
  - Inputs: `canonical_tick`, `session_warp_factor`
  - Output: deterministic warp-time value

## Runtime integration

- `src/time/time_mapping_engine.py`
  - Deterministic mapping evaluation by `(mapping_id, scope_id, canonical_tick)`
  - Cache rows, time-stamp artifacts, proper-time state updates
- `tools/xstack/sessionx/process_runtime.py`
  - Evaluates time mappings at current canonical tick
  - Persists `domain_value_index` inputs for schedule resolution
  - Integrates schedule tick paths with:
    - `schedule_time_bindings`
    - deterministic domain-time resolver
    - `schedule_domain_evaluations` merge

## Schedule-domain behavior

- Non-canonical schedules fire when:
  - `domain_time_value >= target_time_value`
- Execution remains anchored to canonical tick ordering.
- Stable ordering enforced by `schedule_id`/tick sorting in `schedule_engine`.

## Proper-time profile hook

- Proper-time accumulation is persisted in `proper_time_state`.
- Mapping activation is policy/profile controlled through registries and model bindings.

## Epistemic time

- Knowledge receipts remain canonical (`received_tick`).
- Derived temporal stamps are produced as artifacts; they do not mutate truth.

## Proof and replay

- Control proof bundle now includes:
  - `time_mapping_hash_chain`
  - `schedule_domain_evaluation_hash`
- Replay tool added:
  - `tools/time/tool_replay_time_window.py`
  - verifies hash-chain regeneration and schedule/proper-time consistency.

## Enforcement updates

- RepoX strict gates:
  - `INV-TIME-MAPPING-MODEL-ONLY`
  - `INV-NO-CANONICAL-TICK-MUTATION`
  - `INV-SCHEDULE-DOMAIN-RESOLUTION-DETERMINISTIC`
- AuditX strict promotions:
  - `E232_DIRECT_TIME_WRITE_SMELL`
  - `E233_IMPLICIT_CIVIL_TIME_SMELL`
  - existing `E229/E230/E231` retained as strict blockers

## Readiness

Baseline is ready for LOGIC timer semantics via schedule + temporal-domain mapping, without introducing a global clock subsystem or changing canonical tick order.

## Gate Status (2026-03-04)

- RepoX STRICT: PASS
- AuditX STRICT: FAIL (existing promoted blockers `E179_INLINE_RESPONSE_CURVE_SMELL` in non-TEMP modules)
- TestX TEMP-1 targeted set: PASS
  - `test_proper_time_mapping_deterministic`
  - `test_civil_time_mapping_deterministic`
  - `test_schedule_domain_binding`
  - `test_no_canonical_tick_mutation`
  - `test_cross_platform_time_hash_match`
- XStack STRICT: REFUSAL due pre-existing branch-wide failures outside TEMP-1 scope
  - CompatX strict findings/refusals
  - Session boot smoke refusal
  - AuditX promoted blockers
  - TestX branch-wide failures
  - Packaging validation refusal
