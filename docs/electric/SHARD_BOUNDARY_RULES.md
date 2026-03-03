# Shard Boundary Rules

Status: Authoritative (ELEC-5)  
Series: ELEC-5  
Date: 2026-03-03

## 1) Scope

These rules govern cross-shard electrical bundle transfers for ELEC E0/E1.

## 2) Allowed Cross-Shard Topology

Cross-shard electrical edges are valid only when:

- edge endpoints are explicit boundary nodes
- each endpoint declares deterministic shard ownership
- transfer executes on synchronized tick boundary

If these conditions are not met, connection/tick is refused.

## 3) Boundary Node Contract

Boundary nodes must be explicitly marked in node/edge extensions:

- shard id source (`shard_id`)
- boundary marker (`boundary_node = true`)

No implicit shard crossing is permitted.

## 4) Runtime Mutation Constraints

- No direct cross-shard micro solver calls are allowed from electrical runtime.
- Cross-shard electrical transfer is represented as boundary transfer artifacts and proof hashes.
- All authoritative mutation remains process-only.

## 5) Boundary Transfer Artifacts

For each valid cross-shard transfer edge, runtime records deterministic boundary rows:

- graph/edge IDs
- source and target shard IDs
- transferred bundle components (`P`, `Q`, `S`)
- tick and deterministic fingerprint

Rows are replayable and proof-integrated.

## 6) Determinism and Fairness

- transfer ordering is stable by `(graph_id, edge_id)`
- no wall-clock participation
- refusal/degradation events are logged through decision/provenance surfaces
