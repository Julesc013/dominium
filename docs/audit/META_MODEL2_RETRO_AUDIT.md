# META-MODEL-2 Retro Consistency Audit

Date: 2026-03-03
Scope: FlowSystem quantity representation, coupled-quantity approximations, migration readiness.

## 1) Current FlowChannel Quantity Usage

Observed canonical `FlowSystem` channel shape in [schema/core/flow_channel.schema](../../schema/core/flow_channel.schema):

- `quantity_id` is required and singular.
- No first-class multi-component quantity bundle declaration exists.

Observed runtime in [src/core/flow/flow_engine.py](../../src/core/flow/flow_engine.py):

- `normalize_flow_channel()` requires `quantity_id`.
- `tick_flow_channels()` executes scalar transfer (`transferred_amount`, `lost_amount`) only.
- Deterministic ordering is by `channel_id` and stable tie behavior is already present.

Observed event schema in [schema/core/flow_transfer_event.schema](../../schema/core/flow_transfer_event.schema):

- Emits only scalar `transferred_amount` and `lost_amount`.
- No per-component transfer/loss map.

## 2) Existing Coupled-Quantity Approximations / Hacks

1. `process.flow_adjust` model output path in [tools/xstack/sessionx/process_runtime.py](../../tools/xstack/sessionx/process_runtime.py):
   - Stores adjustments as `(channel_id, quantity_id) -> accumulated_delta` rows.
   - Uses `signal_channel.extensions["model_adjust.<quantity_id>"]` as auxiliary storage.
   - Works for per-quantity deltas but has no explicit bundle contract.

2. Model input `flow_quantity` in `process.model_evaluate_tick`:
   - Uses ad-hoc `inputs.flow_quantities` map and limited channel extension lookups.
   - No typed selector for bundle components.

3. Domain-level coupling is currently represented by parallel independent quantities/channels rather than an explicit coupled vector payload.

## 3) Backward-Compatible Migration Plan

1. Add `quantity_bundle` and `component_policy` schemas and registries.
2. Upgrade `flow_channel` + `flow_transfer_event` to additive v1.1.0 fields:
   - `quantity_bundle_id`, component policy refs, component transfer/loss maps.
3. Preserve legacy behavior exactly when bundle fields are absent:
   - scalar channel semantics remain unchanged.
4. Treat legacy scalar channel as implicit bundle of size 1 internally (adapter path only, no breaking content rewrite required).
5. Extend model/process flow input-output path to support component selectors and deterministic per-component adjustments.
6. Add RepoX/AuditX rules to discourage parallel-channel coupling hacks once bundle path exists.

## 4) Determinism / Risk Notes

- No wall-clock dependency introduced by migration plan.
- Flow ordering and budget degradation remain channel-id sorted and deterministic.
- Component maps must be canonicalized by sorted `quantity_id` keys before hashing/events.
- Legacy save compatibility depends on additive optional fields and CompatX version support updates.
