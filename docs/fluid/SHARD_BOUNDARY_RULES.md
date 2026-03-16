Status: DERIVED
Last Reviewed: 2026-03-16
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: DOC-CONVERGENCE
Replacement Target: patched document aligned to current canon ownership and release scope

# FLUID Shard Boundary Rules

## Patch Notes

- Current status: partially aligned to the Constitutional Architecture and release-freeze documentation set.
- Required updates: documentation surface exists, but current canon ownership is not explicit
- Cross-check with: `docs/audit/CANON_MAP.md` and `docs/audit/DOC_DRIFT_MATRIX.md`.


Status: BASELINE
Last Updated: 2026-03-04
Scope: FLUID-3 distributed/sharded boundary contract.

## 1) Cross-Shard Pipe Contract

- Cross-shard pipes are represented only through declared boundary nodes.
- A boundary node is the only legal source/sink for inter-shard fluid transfer.
- Direct reads of foreign shard tank/leak/burst runtime state are forbidden.

## 2) Boundary Transfer Artifacts

- Cross-shard fluid transfer must be serialized as boundary transfer artifacts.
- Transfer artifact ordering is deterministic by:
  1. `tick`
  2. `from_shard_id`
  3. `to_shard_id`
  4. `boundary_node_id`
  5. `transfer_id`
- Receiving shard applies artifacts via process-mediated mutation only.

## 3) Leak/Burst Propagation Across Shards

- Leak/burst consequences do not propagate cross-shard implicitly.
- Any cross-shard consequence requires an explicit boundary event artifact.
- Silent cascade across shard boundaries is forbidden.

## 4) Deterministic Merge Rule

- Boundary artifacts are merged by canonical sort order before solve commit.
- Tie-break behavior must be deterministic and independent of thread interleaving.
- Reenactment must reproduce equivalent boundary artifact sequence hashes.

## 5) Degradation Under Budget Pressure

- Shard-local FLUID degradation is allowed only through logged deterministic sequence:
  1. tick-bucket reduce solve frequency
  2. deterministic subgraph F0 downgrade
  3. defer non-critical model bindings
  4. cap leak evaluations
- Degradation does not permit skipping boundary artifact emission.
