Status: DERIVED
Last Reviewed: 2026-02-27
Supersedes: none
Superseded By: none
Version: 1.0.0
Compatibility: Bound to `docs/canon/constitution_v1.md` and `docs/canon/glossary_v1.md`.
Stability: provisional
Future Series: DOC-ARCHIVE
Replacement Target: legacy reference surface retained without current binding authority

# Logistics Graph

## Purpose
Define deterministic MAT-4 meso logistics substrate contracts for node/edge transport, routing, manifest flow, and conservation-safe stock transfer.

## Scope Constraints
- No micro vehicle simulation.
- No pathfinding with continuous geometry.
- No traffic-wave or economy pricing simulation.
- No crafting or inventory gameplay loops.

## Logistics Worldview
- Logistics is a meso representation over `nodes`, `edges`, manifests, commitments, and event logs.
- Outside ROI, transport is authoritative stock transfer with deterministic delay/loss accounting.
- Micro transport actors are deferred refinements (future MOB series) and must be derivable from manifest provenance.

## Canonical Graph Model
- `LogisticsNode`
  - typed infrastructure endpoint (`site`, `depot`, `factory`, `port`, `station`, `warehouse`)
  - deterministic location reference and optional storage capacity
- `LogisticsEdge`
  - directed route between nodes
  - mode-tagged (`road`, `rail`, `sea`, `air`, `space`, `abstract`)
  - fixed capacity, deterministic delay in ticks, optional loss/cost coefficients
- `RoutingRule`
  - deterministic tie-break policy
  - optional multi-hop behavior and constraints

## Deterministic Routing + Flow
- Route selection is deterministic for identical graph/manifests/rules.
- Tie-breaks are deterministic (`edge_id` lexical order minimum baseline).
- Flow progression advances per tick in stable manifest order (`manifest_id`).
- No nondeterministic optimization kernels are allowed in authoritative flow state.

## Ledger Integration
- Node stock transfer must not create/destroy invariant quantity channels silently.
- Loss is process-accounted and policy-classified through explicit exception ledger entries.
- Process boundaries remain authoritative mutation boundaries (A2).

## Null/Scale Compatibility
- Null universe may run with empty logistics graph/manifest registries.
- Procedural and mega-scale universes can shard graph domains while preserving deterministic manifest identity and replay order.

## Constitutional Alignment
- A1 Determinism: route choice, manifest progression, and loss accounting are order-stable.
- A2 Process-only mutation: stock moves only through logistics processes.
- A6 Provenance: shipment depart/arrive/lost events are canonical and reenactable.
- A9 Pack-driven integration: routing rules and graphs are registry-driven.
