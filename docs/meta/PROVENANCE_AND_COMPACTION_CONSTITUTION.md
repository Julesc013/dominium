Status: CANONICAL
Last Reviewed: 2026-03-05
Supersedes: none
Superseded By: none
Version: 1.0.0
Compatibility: Bound to `docs/canon/constitution_v1.md` and `docs/canon/glossary_v1.md`.
Stability: provisional
Future Series: DOC-CONVERGENCE
Replacement Target: canon-aligned documentation set for convergence and release preparation

# Provenance and Compaction Constitution (PROV-0)

## 1. Purpose
Define deterministic event-sourcing provenance rules and deterministic compaction constraints so storage remains bounded without compromising canonical replay equivalence.

## 2. Canonical Event Sourcing Rule
- Authoritative state evolution is event-sourced.
- Canonical state transitions are represented as canonical event rows and are never silently discarded.
- Derived artifacts may be compacted only when deterministic recomputation is guaranteed.

## 3. Event Classes

### 3.1 Canonical Events (Never discard)
Canonical class includes, at minimum:
- process-mediated state mutation events
- `energy_ledger_entry`
- `boundary_flux_event`
- fault/leak/burst/relief and related containment failure records
- `time_adjust_event`
- branch/fork records
- `compaction_marker`

### 3.2 Derived Artifacts (Compactable)
Derived class includes, at minimum:
- explain artifacts
- inspection snapshots
- derived summaries/aggregate views
- cached model outputs
- non-authoritative diagnostics and analytics views

## 4. Compaction Rules

### 4.1 Derived-only compaction
- Only artifacts classified as `derived` and `compaction_allowed=true` may be removed/rewritten by compaction.
- Compaction of canonical events is forbidden.

### 4.2 Canonical grouping
- Canonical events may be grouped/re-encoded into deterministic blocks, but semantic event retention is mandatory.
- Lossy canonical compaction is forbidden.

### 4.3 Marker requirement
Every compaction operation must emit `compaction_marker` as a canonical RECORD with:
- compaction window `[start_tick, end_tick]`
- pre-compaction anchor hash
- post-compaction anchor hash
- shard identifier

## 5. Replay Guarantees
- Replay from genesis and replay from any accepted compaction anchor must converge to identical TruthModel state hash.
- Replay divergence after compaction is a contract failure.
- Compaction marker anchors are part of proof witness coverage.

## 6. Shard Discipline
- Shards compact independently under deterministic ordering.
- Each shard emits its own ordered compaction marker chain.
- Cross-shard proof envelopes must reference shard compaction anchors when compaction occurred.

## 7. Compression Policy

Allowed:
- deterministic delta encoding of canonical events
- deterministic binary/canonical serialization
- deterministic removal/aggregation of derived artifacts

Forbidden:
- lossy canonical event deletion
- wall-clock driven compaction behavior
- nondeterministic compaction ordering

## 8. Determinism and Governance
- Compaction ordering keys are deterministic (`shard_id`, `start_tick`, `end_tick`, marker id).
- Compaction decisions are policy-driven and auditable.
- Strict enforcement must block:
  - canonical-event compaction
  - unclassified artifact compaction
  - compaction operations without emitted marker anchors

## 9. Integration Contract
- Proof bundles include:
  - compaction marker hash chain
  - compaction pre-anchor hash
  - compaction post-anchor hash
- Replay tooling must support anchor-based verification.
- Classification registry is authoritative for compaction eligibility decisions.
