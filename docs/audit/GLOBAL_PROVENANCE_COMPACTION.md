# GLOBAL PROVENANCE & COMPACTION REVIEW

Date: 2026-03-05
Scope: `GLOBAL-REVIEW-REFRACTOR-1 / Phase 6`

## Inputs Reviewed
- Provenance classification registry: `data/registries/provenance_classification_registry.json`
- Compaction engine: `src/meta/provenance/compaction_engine.py`
- Replay-from-anchor tooling: `tools/meta/tool_verify_replay_from_anchor.py`
- Stress harness: `tools/meta/tool_provenance_stress.py`

## Verification Results
- Provenance strict tests passed:
  - `test_canonical_events_not_compacted`
  - `test_derived_artifacts_compactable`
  - `test_replay_after_compaction_matches_hash`
  - `test_cross_shard_compaction_deterministic`
  - `test_compaction_marker_hash_stable`
- Stress compaction run passed with deterministic fingerprint:
  - `71ed59dbf25850efd269aa75862f9dd6a755557c5fa6189403c1bc02ce0b7dc6`
- Replay-from-anchor now validates both:
  - latest-state marker replay consistency
  - historical anchor consistency for non-latest markers in long stress windows

## Issue Found and Repaired
- Issue:
  - Replay verification compared a selected marker's stored replay hash directly against the final full-state replay hash.
  - This failed for deterministic stress runs selecting non-latest markers, even when provenance remained valid.
- Repair:
  - Added deterministic historical-anchor projection support in `verify_replay_from_compaction_anchor`.
  - Verification now accepts either:
    - direct current-state replay hash match, or
    - historical anchor replay hash match at `marker_end_tick`.

## Canonical vs Derived Safety
- Canonical event projections remain immutable under compaction checks.
- Derived artifact removal remains classified and bounded by provenance registry policy.
- Marker chain/anchors remain hashable and deterministic.

## Outcome
- Phase 6 stop conditions not triggered.
- Provenance compaction and replay discipline validated for cross-shard stress workloads.
