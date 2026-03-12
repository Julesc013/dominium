Status: DERIVED
Version: 1.0.0
Last Reviewed: 2026-02-16
Compatibility: Bound to Observation Kernel and epistemic policy registries.
Stability: provisional
Future Series: DOC-CONVERGENCE
Replacement Target: patched document aligned to current canon ownership and release scope

# Memory And Fog Of War

## Patch Notes

- Current status: partially aligned to the Constitutional Architecture and release-freeze documentation set.
- Required updates: documentation surface exists, but current canon ownership is not explicit
- Cross-check with: `docs/audit/CANON_MAP.md` and `docs/audit/DOC_DRIFT_MATRIX.md`.


## Purpose
Define deterministic epistemic memory as a policy-governed extension of `PerceivedModel` with no TruthModel storage.

## Core Model

1. `perceived.now` is the current tick projection from Observation Kernel.
2. `perceived.memory` is derived from `perceived.now` only.
3. Memory data is constrained by:
   - channel allow/deny from `EpistemicPolicy`
   - precision already quantized/redacted in `PerceivedModel`
   - retention capacity from `RetentionPolicy`
   - tick-based decay and deterministic eviction.

Pipeline contract:

`Truth x Lens x Law x Authority x EpistemicPolicy -> perceived.now`

`MemoryKernel(perceived.now, retention_policy, decay_model, eviction_rule, tick) -> perceived.memory`

## Memory Forms

1. Episodic events:
   - Process log event rows, signals, and deterministic event IDs.
2. Spatial summaries:
   - Navigation hierarchy observations and site/map summaries.
3. Entity facts:
   - Last observed entity payload by channel/subject key.

## Deterministic Identity And Ordering

1. Memory item ID:
   - `H(owner_subject_id, channel_id, subject_kind, subject_id, source_tick_bucket)`.
2. Source tick bucket:
   - fixed 32-tick buckets (`source_tick // 32`).
3. Stable item ordering:
   - `(channel_id, subject_kind, subject_id, source_tick, memory_item_id)`.
4. Store hash:
   - canonical hash over memory store payload excluding `store_hash` field.

## Decay And Eviction

1. Decay is tick-based only.
   - `ttl_ticks` decreases by simulation tick delta.
   - wall-clock APIs are forbidden.
2. Decay/refresh selection uses registry rules by `(channel_id, subject_kind)` with deterministic wildcard precedence.
3. Eviction is deterministic and registry-defined:
   - `evict.oldest_first`
   - `evict.lowest_priority`
   - `evict.none` (safe only for zero-cap/diagnostic policies).

## Network Safety

1. Minimum requirement:
   - server governs all observation inputs sent to client.
2. Current baseline:
   - clients compute memory locally from server-filtered `perceived.now`.
   - memory `store_hash` is included in memory state and delta metadata for auditability.
3. Truth payloads are never stored or transported as memory.

## Refusal Codes

1. `refusal.ep.policy_missing`
2. `refusal.ep.memory_policy_violation`
3. `refusal.ep.channel_forbidden`
4. `refusal.ep.entitlement_missing`

## Non-Goals

1. No gameplay semantics (morale, trust, fear, etc.).
2. No wall-clock decay.
3. No TruthModel retention.
4. No mode flags.
