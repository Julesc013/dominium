Status: BASELINE
Last Reviewed: 2026-02-28
Scope: ABS-2 NetworkGraph substrate hardening.

# NetworkGraph Standard Baseline

## 1) Schema Versions
- `network_graph`: `1.0.0`
- `network_node`: `1.0.0`
- `network_edge`: `1.0.0`
- `route_query`: `1.0.0`
- `route_result`: `1.0.0`
- `graph_partition`: `1.0.0`

CompatX version registry includes these schema keys and keeps `1.0.0` as current/supported.

## 2) Routing Policies and Determinism
- Policies supported:
  - `route.direct_only`
  - `route.shortest_delay`
  - `route.min_cost_units`
- Deterministic ordering:
  - nodes by `node_id`
  - edges by `(from_node_id,to_node_id,edge_id)`
- Deterministic tie-break:
  - equal-cost paths resolve to lexicographically smallest edge-id sequence.
- Route query output is canonicalized with:
  - ordered `path_node_ids`
  - ordered `path_edge_ids`
  - deterministic fingerprint and cache keys.

## 3) Partitioning Support
- `graph_partition` provides:
  - node-to-shard ownership
  - edge-to-shard ownership
  - cross-shard boundary nodes
- Routing emits a derived cross-shard route plan artifact with:
  - ordered shard-local segments
  - ordered boundary transitions
  - deterministic plan fingerprint
- No distributed execution semantics were introduced; this is structural SRZ-ready metadata.

## 4) Inspection and Overlay Integration
- Inspection section registry includes:
  - `section.networkgraph.summary`
  - `section.networkgraph.route`
  - `section.networkgraph.capacity_utilization`
- Overlay behavior:
  - node glyphs
  - directed edge lines
  - route-edge highlight when route section data is present
- Overlays are derived from inspection/perceived payloads and do not mutate TruthModel.

## 5) Migration and Hardening
- MAT logistics routing uses `src/core/graph/routing_engine.py` APIs.
- Existing logistics refusal semantics remain mapped to:
  - `refusal.logistics.invalid_route`
- Graph tooling added:
  - `tools/core/tool_graph_validate.py`
  - `tools/core/tool_route_query.py`
- Enforcement added:
  - RepoX `INV-NETWORKGRAPH-ONLY`
  - AuditX analyzers:
    - `RoutingDuplicationSmell`
    - `NonDeterministicRoutingSmell`

## 6) Extension Guidance
- INT:
  - model interior volumes/portals as `NetworkGraph` node/edge payloads.
- MOB:
  - model tracks/lanes/links as graph edges with domain payload refs.
- SIG:
  - carry signal topology on graph edges and route policies.
- INF:
  - model utility and institutional networks by payload typing, not new graph engines.

Use `NetworkGraph` + `FlowSystem` wrappers for domain-specific behavior; do not create parallel routing substrates.

## 7) Gate Snapshot (2026-02-28)
1. RepoX PASS
   - command: `py -3 tools/xstack/repox/check.py --repo-root . --profile STRICT`
   - result: `status=pass`, findings=0
2. AuditX run
   - command: `py -3 tools/xstack/auditx/check.py --repo-root . --profile STRICT`
   - result: `status=pass`, findings=959 (warn-level findings present)
3. TestX PASS
   - command: `py -3 tools/xstack/testx/runner.py --repo-root . --profile FAST --cache off --subset testx.core.network_graph_deterministic_ordering,testx.core.routing_deterministic_tie_break,testx.core.routing_cache_reuse,testx.core.partition_route_plan_deterministic,testx.core.graph_overlay_render_model_hash_stable,testx.materials.logistics_route_equivalence,testx.materials.logistics_migration_behavior_equivalence`
   - result: `status=pass`, selected_tests=7
4. strict build PASS
   - command: `py -3 tools/setup/build.py --repo-root . --bundle bundle.base.lab --out build/dist.strict.abs2 --cache on --format json`
   - result: `result=complete`
5. ui_bind --check PASS
   - command: `py -3 tools/xstack/ui_bind.py --repo-root . --check`
   - result: `result=complete`, checked_windows=21
