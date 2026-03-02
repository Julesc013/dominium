# MOB2 Retro-Consistency Audit

Status: AUDIT
Date: 2026-03-02
Scope: MOB-2 GuideGeometry to NetworkGraph integration.

## 1) Existing track/road graph structures outside NetworkGraph

1. No separate canonical `track_graph` or `road_graph` state collections exist in runtime.
2. Canonical graph substrate already exists in `state["network_graphs"]` through `src/core/graph/network_graph_engine.py`.
3. Mobility graph semantics are currently missing: node/edge payload kinds are generic and not mobility-specialized.

## 2) Existing ad-hoc routing logic

1. Deterministic routing substrate already exists in `src/core/graph/routing_engine.py`.
2. `tools/xstack/sessionx/process_runtime.py` currently has no mobility-specific route process; route payloads are mostly inspection-side.
3. `process.formalization_promote_networked` currently seeds a placeholder two-node graph that is not derived from GuideGeometry segments/junctions.

## 3) Existing promotion path gaps

1. `process.formalization_promote_networked` mutates `network_graphs` directly in-process but does not create mobility payload bindings.
2. No canonical mobility binding rows exist (`formalization_id -> graph_id/node_ids/edge_ids`).
3. No switch state machine collection is maintained for mobility junction switches.

## 4) Migration plan to MOB-2 substrate

1. Introduce mobility payload schemas:
   - `mobility_node_payload`
   - `mobility_edge_payload`
   - `mobility_network_binding`
2. Add mobility network registries:
   - node kinds
   - edge kinds
   - mobility max speed policies
3. Add deterministic mobility network engine to map:
   - GuideGeometry endpoints/junctions -> NetworkGraph nodes
   - GuideGeometry segments -> NetworkGraph edges
4. Replace placeholder formalization promotion graph construction with:
   - `process.mobility_network_create_from_formalization`
   - `process.formalization_promote_networked` delegating to mobility mapping.
5. Add switch control path:
   - `process.switch_set_state`
   - deterministic StateMachine transitions only
6. Route through core routing engine with switch-disabled edge filtering and deterministic cache artifacts.

## 5) Deprecation targets

- Placeholder graph seed in `process.formalization_promote_networked`.
- Any future mobility edge enable/disable writes outside switch state machine/process path.
- Any mobility routing helper that bypasses `src/core/graph/routing_engine.py`.
