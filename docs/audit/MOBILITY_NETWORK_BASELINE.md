# MOBILITY_NETWORK_BASELINE

Status: BASELINE
Last Updated: 2026-03-02
Scope: MOB-2 GuideGeometry to MobilityNetworkGraph integration.

## 1) Constitutional Rules Implemented

- Mobility connectivity is authored as `NetworkGraph` payload specialization:
  - nodes use `mobility_node_payload`
  - edges use `mobility_edge_payload`
- Authoritative mutations are process-only:
  - `process.mobility_network_create_from_formalization`
  - `process.mobility_network_edit`
  - `process.switch_set_state`
  - `process.mobility_route_query`
- Deterministic ordering and identities:
  - deterministic graph/node/edge/binding IDs
  - sorted traversal by canonical IDs
  - deterministic routing tie-break policy
- Budgeted/degrade behavior:
  - bounded network edit operations per tick
  - bounded route query count per tick
  - cache-first route reuse
  - explicit refusal + decision logging on budget exhaustion

## 2) GuideGeometry -> NetworkGraph Mapping

- Inputs:
  - `guide_geometries`
  - `mobility_junctions`
  - `geometry_derived_metrics`
  - formalization lifecycle state (`formal` or `networked`)
- Mapping:
  - junctions/endpoints map to graph nodes
  - guide segments map to directed edges with mobility payload
  - edge payload carries geometry/spec/speed-policy references
  - mobility binding row links formalization to graph/node/edge IDs
- Output artifacts:
  - `network_graphs` row
  - `mobility_network_bindings` row
  - switch state-machine rows for switch nodes

## 3) Switch Mechanics

- Switch nodes are modeled as mobility nodes with `node_kind="switch"`.
- Each switch node is bound to a deterministic state machine:
  - state value is active outgoing `edge_id`
  - transitions are explicit and deterministic
  - transition execution routes only through `process.switch_set_state`
- Route availability is filtered by active switch state before routing.
- Switching emits deterministic switch events with provenance fields.

## 4) Routing Behavior

- Routing runs through ABS routing engine (`query_route_result`) over switch-filtered graph.
- Routing policy defaults to `route.shortest_delay` and deterministic edge-id tie-break.
- Disabled edges from switch state are excluded from route candidate space.
- Route results and cache state are derived artifacts:
  - `mobility_route_results`
  - `mobility_route_cache_state`
- Refusals:
  - `refusal.mob.no_route`
  - `refusal.mob.network_invalid`
  - `refusal.mob.fidelity_denied`

## 5) UX/Inspection Surfaces

- Action affordances added for:
  - promote network creation
  - inspect route
  - toggle switch
  - inspect mobility node/edge (graph inspection path)
- Inspection sections added:
  - `section.mob.network_summary`
  - `section.mob.route_result`
- Overlay metadata includes:
  - route highlighting
  - switch-state glyph labels
  - spec-missing edge indicators

## 6) Integration Points

- SPEC:
  - optional spec enforcement via `require_spec` on network creation
  - edge payload includes `spec_id` and speed-policy fields
- FORM:
  - formalization network promotion now creates/updates mobility network artifacts deterministically
- CTRL:
  - all create/edit/switch/route flows are process+intent mediated
  - budget downgrades/refusals are logged
- ABS:
  - `NetworkGraph` substrate and routing engine reused directly
- RND/Inspection:
  - mobility sections and overlays are derived/read-only

## 7) Performance Guarantees

- No micro vehicle solver introduced in MOB-2.
- No congestion/interlocking solver introduced in MOB-2.
- No wall-clock dependence in authoritative mutation/routing.
- Deterministic bounded work:
  - route query cap per tick
  - network edit cap per tick
  - deterministic degrade/refusal order

## 8) Extension Points

- MOB-4 macro itineraries:
  - macro commitments can reference mobility graph edge IDs and route policy IDs.
- MOB-5 congestion:
  - edge payload already exposes capacity fields for future occupancy/cost layers.
- MOB-6 micro solvers:
  - micro kinematics can consume selected mobility edge/guide constraints in ROI only.
- MOB-8 interlocking/signals:
  - switch state machines and route filtering provide baseline interlocking anchors.

## 9) Gate Runs (2026-03-02)

- RepoX:
  - command: `python tools/xstack/repox/check.py --repo-root . --profile STRICT`
  - status: `pass` (warn-only findings present; no refusal)
- AuditX:
  - command: `python tools/xstack/auditx/check.py --repo-root . --profile STRICT`
  - status: `pass` (scan executed; findings reported)
- TestX (MOB-2 subset):
  - command: `python tools/xstack/testx/runner.py --repo-root . --profile STRICT --subset testx.mobility.network_create_deterministic,testx.mobility.switch_state_changes_route_availability,testx.mobility.routing_deterministic_tie_break,testx.mobility.spec_noncompliance_refusal,testx.mobility.network.overlay_render_hash_stable`
  - status: `pass` (5/5)
- strict build:
  - command: `python tools/setup/build.py --repo-root . --bundle bundle.base.lab --out build/dist.strict.mob2 --cache on --format json`
  - status: `pass` (`result=complete`)
- topology map update:
  - command: `python tools/governance/tool_topology_generate.py --repo-root . --out-json docs/audit/TOPOLOGY_MAP.json --out-md docs/audit/TOPOLOGY_MAP.md`
  - status: `complete` (`node_count=2341`, `edge_count=99284`)

