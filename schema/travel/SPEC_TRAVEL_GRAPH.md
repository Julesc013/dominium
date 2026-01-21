# SPEC TRAVEL GRAPH (TRAVEL0)

Status: draft.
Version: 1.0
Scope: canonical travel graph nodes and topology.

## Travel Node
A Travel Node represents a location or travel state that can be entered.

Required fields:
- node_id (stable)
- domain_ids (one or more)
- existence_state requirements (EXIST0)
- visitability requirements (DOMAIN4)

Nodes may represent:
- points (room, city, station)
- volumes (planet surface, region)
- abstract states (orbit, hyperspace)

## Graph Topology
- Graph is explicit and finite for any loaded subset.
- No implicit edges or hidden transitions.
- Node ordering and adjacency are deterministic.

## Determinism Rules
- Graph identity is stable across runs given identical data.
- Node IDs are stable and unique.
- Graph changes require explicit schema/data updates.

## Integration Points
- DOMAIN: nodes reference domain volumes.
- EXISTENCE: nodes declare required existence states.
- VISITABILITY: nodes declare required contracts.
- LAW: edges and nodes are law-gated.
