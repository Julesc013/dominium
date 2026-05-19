Status: DERIVED
Last Reviewed: 2026-02-16
Supersedes: none
Superseded By: none
Version: 1.0.0
Scope: ED-1/4 deterministic epistemic memory baseline.
Stability: provisional
Future Series: DOC-CONVERGENCE
Replacement Target: canon-aligned documentation set for convergence and release preparation

# Epistemic Memory Baseline

## Policies Supported

1. `ep.retention.none`
2. `ep.retention.session_basic`
3. `ep.retention.long` (stub)

Retention now binds deterministic decay + eviction references.

## Decay Models

1. `ep.decay.none`
2. `ep.decay.session_basic`
3. `ep.decay.session_strict`
4. `ep.decay.long_stub`

All decay is tick-based only.

## Eviction Rules

1. `evict.none`
2. `evict.oldest_first`
3. `evict.lowest_priority`

## Runtime Integration

1. Observation kernel now resolves:
   - epistemic policy
   - retention policy
   - decay model
   - eviction rule
2. Perceived output includes deterministic memory store payload:
   - `perceived.memory.items`
   - `perceived.memory.store_hash`
3. Memory state persists per client/view and is propagated through multiplayer perceived-delta metadata as audit fields.

## Determinism And Safety

1. Memory IDs use deterministic source-tick buckets.
2. TTL decay is based on simulation tick delta only.
3. Eviction uses deterministic sorted ranking.
4. Memory subsystem is Perceived-only and does not ingest/store TruthModel payloads.

## Test Coverage Summary

1. `test_memory_determinism`
2. `test_memory_policy_channel_forbidden`
3. `test_memory_eviction_deterministic`
4. `test_memory_decay_tick_based`
5. `test_memory_store_hash_audit`

## Governance Hooks

1. RepoX invariants:
   - `INV-MEMORY-NO-TRUTH`
   - `INV-MEMORY-TICK-BASED`
2. AuditX analyzers:
   - `E22_MEMORY_TRUTH_LEAK_SMELL`
   - `E23_MEMORY_NONDETERMINISM_SMELL`

## Extension Points

1. Long-memory historical models (policy+schema only in this baseline).
2. Trust/communication/history layers can consume memory items without changing Truth semantics.
3. Optional memory delta transport remains available for future optimization.
