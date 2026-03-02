# Mobility NetworkGraph Doctrine

Status: CANONICAL
Last Updated: 2026-03-02
Scope: MOB-2 deterministic mapping from GuideGeometry to NetworkGraph.

## 1) Purpose

MobilityNetworkGraph is a specialization of `NetworkGraph` using mobility payload contracts. It is the authoritative connectivity substrate for routing, switch state, and future schedule/signal/congestion systems.

## 2) Graph Specialization

MobilityNetworkGraph uses canonical NetworkGraph containers with payload schema specialization:

- Node payload schema: `dominium.schema.mobility.mobility_node_payload`
- Edge payload schema: `dominium.schema.mobility.mobility_edge_payload`

Validation remains `strict` by default unless explicit policy degrades to `warn`.

## 3) Node Payload Semantics

`mobility_node` payload rows use `node_kind`:

- `endpoint`
- `junction`
- `station`
- `switch`
- `waypoint`

Node payload may reference:

- `parent_spatial_id`
- `position_ref`
- `junction_id`
- `state_machine_id` (required for switch nodes)
- `tags` and `extensions`

## 4) Edge Payload Semantics

`mobility_edge` payload rows use `edge_kind`:

- `track`
- `road`
- `lane`
- `corridor`
- `orbit_link`
- `custom`

Each edge payload references:

- `guide_geometry_id`
- optional `spec_id`
- optional `capacity_units`
- optional `max_speed_policy_id`
- `tags` and `extensions`

## 5) GuideGeometry Mapping

Deterministic mapping rules:

1. Endpoints and junction anchors become nodes.
2. Each GuideGeometry segment becomes one or more directed edges.
3. Node and edge identities are deterministic hashes of:
   - `formalization_id`
   - geometry/junction identifiers
   - canonical endpoint ordering
4. Ordering:
   - geometries sorted by `geometry_id`
   - junctions sorted by `junction_id`
   - generated nodes sorted by `node_id`
   - generated edges sorted by `(from_node_id, to_node_id, edge_id)`

## 6) Junction and Switch Semantics

- Junction nodes represent passive connectivity anchors.
- Switch nodes bind to deterministic state machines:
  - state id expresses active outgoing edge
  - transitions are process-triggered only
  - no direct edge activation bypass
- Switch operations use control-plane process path `process.switch_set_state` and may carry
  diegetic `action_surface_id` / `task_ref` evidence in extensions for provenance.
- Disabled/non-active outgoing edges are unavailable to routing queries.

## 7) Formalization Promotion Contract

`FORMAL -> NETWORKED` promotion requires process path:

1. `process.mobility_network_create_from_formalization`
   - validates formalization is at least `formal`
   - maps GuideGeometry into NetworkGraph rows
   - creates `mobility_network_binding`
2. `process.formalization_promote_networked`
   - records lifecycle transition/event
   - binds `network_graph_ref`

Inference candidates remain derived-only until accepted; promotion never mutates inferred-only artifacts directly.

## 8) Deterministic Routing Assumptions

- Routing uses ABS deterministic routing engine.
- Tie-break remains deterministic lexicographic edge path.
- Switch state filtering is deterministic and inspectable.
- Route cache entries are derived artifacts keyed by canonical graph/policy/constraint hashes.

## 9) Performance Constitution

- Global micro movement remains forbidden.
- MOB-2 computes connectivity/routing only; no micro solver.
- Routing costs are budgeted with explicit deterministic degradation:
  - cache hit reuse first
  - bounded query count next
  - explicit refusal when limits are exceeded

## 10) Integration Boundaries

- CTRL: all create/edit/switch/routing operations are process/control-plane mediated.
- FORM: promotion to networked emits formalization events and provenance.
- SPEC: edge payload stores spec references and max-speed policy ids.
- RND/Inspection: overlays and sections expose nodes/edges/switch state/route result without truth mutation.

## 11) Non-Goals (MOB-2)

- No vehicle micro physics.
- No congestion solver.
- No interlocking/signal logic.
- No wall-clock dependence or nondeterministic switching.

## 12) UX + Inspection Hooks

Mobility network UX affordances are data-driven and control-plane mediated:

- `interaction.promote_to_network`
- `interaction.inspect_route`
- `interaction.toggle_switch`
- `interaction.inspect_mobility_node`
- `interaction.inspect_mobility_edge`

Inspection snapshots expose mobility-focused sections:

- `section.mob.network_summary`
- `section.mob.route_result`

Render overlays for graph inspection include:

- edge/route line overlays following graph edges
- switch node state glyph labels
- spec-missing edge indicators
