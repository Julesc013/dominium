# Provenance Baseline

Status: CANONICAL
Last Updated: 2026-03-05
Scope: PROV-0 event sourcing and deterministic compaction discipline.

## 1) Classification Summary

Canonical (non-compactable) coverage includes:

- `artifact.energy_ledger_entry`
- `artifact.boundary_flux_event`
- `artifact.time_adjust_event`
- `artifact.exception_event`
- `artifact.fault_event`
- `artifact.leak_event`
- `artifact.burst_event`
- `artifact.relief_event`
- `artifact.branch_event`
- `artifact.compaction_marker`

Derived (compactable) coverage includes:

- `artifact.explain` and explain specializations
- `artifact.inspection_snapshot`
- `artifact.model_evaluation_result`
- observation-oriented inspection/measurement artifact types

Registry source:

- `data/registries/provenance_classification_registry.json`

## 2) Compaction Policy

Compaction is deterministic and derived-only:

- engine: `src/meta/provenance/compaction_engine.py`
- window validation blocks compaction when:
  - open branches intersect the window
  - unsealed proof windows intersect the window
- raw derived rows inside window are compacted; canonical rows are retained
- each compaction writes a canonical `compaction_marker`
- hash anchors are updated:
  - `compaction_marker_hash_chain`
  - `compaction_pre_anchor_hash`
  - `compaction_post_anchor_hash`

## 3) Replay Guarantees

Replay-from-anchor integration is in place:

- tool: `tools/meta/tool_verify_replay_from_anchor`
- proof schema includes compaction witness fields
- replay verification requires marker-consistent replay hash and deterministic chain continuity

## 4) Storage Characteristics

Stress harness:

- tool: `tools/meta/tool_provenance_stress`
- deterministic multi-shard event generation
- periodic compaction windows
- deterministic anchor selection and replay verification
- metrics emitted:
  - storage growth permille
  - compaction effectiveness permille
  - generated vs removed derived rows
  - replay cost units

## 5) Enforcement Summary

RepoX hard-gate coverage added:

- `INV-CANONICAL-EVENT-NOT-DISCARDED`
- `INV-DERIVED-ONLY-COMPACTABLE`
- `INV-COMPACTION-MARKER-REQUIRED`

AuditX analyzers added:

- `E239_CANONICAL_ARTIFACT_COMPACTION_SMELL`
- `E240_UNCLASSIFIED_ARTIFACT_SMELL`
- `E241_MISSING_COMPACTION_MARKER_SMELL`

TestX coverage added:

- `test_canonical_events_not_compacted`
- `test_derived_artifacts_compactable`
- `test_replay_after_compaction_matches_hash`
- `test_cross_shard_compaction_deterministic`
- `test_compaction_marker_hash_stable`

## 6) Gate Snapshot

Executed during PROV-0 closeout:

- RepoX STRICT: blocked by `INV-WORKTREE-HYGIENE` while changes were in-flight; provenance-specific refusals resolved after registry/topology updates.
- AuditX STRICT: fails on pre-existing promoted `E179_INLINE_RESPONSE_CURVE_SMELL` findings outside PROV-0 scope.
- TestX provenance subset: pass (`5/5`).
- Provenance stress harness: pass (`result=complete`).
- Topology map: regenerated (`docs/audit/TOPOLOGY_MAP.json`, `docs/audit/TOPOLOGY_MAP.md`).

## 7) Readiness

PROV-0 baseline is ready for chemistry expansion with:

- deterministic event-sourcing separation,
- explicit canonical/derived provenance classes,
- replay-safe derived compaction,
- shard-local compaction anchors and proof continuity.
