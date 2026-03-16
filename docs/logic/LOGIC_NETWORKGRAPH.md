Status: DERIVED
Last Reviewed: 2026-03-16
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: DOC-CONVERGENCE
Replacement Target: canon-aligned documentation set for convergence and release preparation

# LOGIC NetworkGraph

Status: normative
Version: 1.0.0
Depends on: LOGIC-0, LOGIC-1, LOGIC-2, ABS NetworkGraph

## Purpose

`LogicNetworkGraph` is the authoritative topology layer for player-built logic wiring, bus links, framed links, and message-carrier links.

It is:
- substrate-agnostic
- deterministic
- a specialization of `core/network_graph.schema`
- the sole canonical topology path for LOGIC evaluation, compilation, and debugging

It is not:
- an evaluation engine
- an electrical solver
- a protocol runtime
- a clock subsystem

## A) Node Types

Canonical node kinds:
- `port_in`
- `port_out`
- `junction`
- `bus_junction`
- `protocol_endpoint`

Canonical `node_type_id` convention:
- `node.logic.port_in`
- `node.logic.port_out`
- `node.logic.junction`
- `node.logic.bus_junction`
- `node.logic.protocol_endpoint`

Node payloads declare topology meaning only. They do not execute behavior.

### Port nodes
- `node.port_in` binds a logic element input port.
- `node.port_out` binds a logic element output port.
- Port nodes should declare `element_instance_id` and `port_id`.

### Junction nodes
- `node.junction` is a fanout or merge point for single-signal links.
- `node.bus_junction` is the equivalent topology point for buses.
- Junctions have no implicit computation or carrier semantics.

### Protocol endpoints
- `node.protocol_endpoint` declares a framed or arbitration-aware boundary.
- Protocol meaning is resolved through registry-defined protocol hooks, not embedded network behavior.

## B) Edge Types

Canonical edge kinds:
- `link`
- `bus_link`
- `protocol_link`
- `sig_link`

Canonical `edge_type_id` convention:
- `edge.logic.link`
- `edge.logic.bus_link`
- `edge.logic.protocol_link`
- `edge.logic.sig_link`

### `edge.link`
- Carries a single typed signal.
- Supports direct port-to-port, port-to-junction, and junction-to-port topology.

### `edge.bus_link`
- Carries a declared bus definition.
- Bus compatibility is validated against bus definitions and encoding rules.

### `edge.protocol_link`
- Carries framed traffic bound to a declared protocol definition.
- Protocol endpoints and framing metadata must match.

### `edge.sig_link`
- Uses SIG-style receipt/message transport semantics.
- Intended for remote, asynchronous, or shard-boundary communication.

## C) Compatibility Rules

### Signal compatibility
- Edge `signal_type_id` must match the attached signal ports.
- Type changes require an explicit transducer seam; implicit coercion is invalid.

### Carrier compatibility
- Carrier identity constrains cost, delay, access, and admissibility.
- Carrier identity must not alter logic semantics.
- Carrier allowances are resolved by policy, registry, or transducer declarations.

### Bus compatibility
- `bus_link` edges must resolve to the same bus definition and encoding expectations at both ends.
- Width and field structure mismatches are invalid.

### Protocol compatibility
- `protocol_link` edges require compatible endpoint declarations.
- `protocol_id` must resolve and match the bound endpoint or explicit adapter path.

## D) Loop Classification

Loop detection is deterministic and mandatory before evaluation.

### Combinational loop
- A strongly connected component whose participating logic elements are purely combinational.
- Forbidden by default.

### Sequential loop
- A strongly connected component whose participating logic elements are storage-bearing only.
- Allowed.

### Mixed loop
- A strongly connected component that mixes combinational and sequential elements.
- Policy-controlled.
- May require forced ROI micro execution or future compiled-stability proof.

Loop classification uses:
- network topology
- deterministic internal element flow expansion
- behavior model kinds from LOGIC-2

No wall-clock sampling or dynamic heuristic is permitted.

## E) Deterministic Ordering

Canonical ordering rules:
- graphs sorted by `graph_id`
- networks sorted by `network_id`
- nodes sorted by `node_id`
- edges sorted by `(from_node_id, to_node_id, edge_id)`
- stable toposort ties broken lexically by `node_id`
- SCC member ordering broken lexically by `node_id`

This ordering is authoritative for:
- validation
- hashing
- compilation inputs
- future evaluation scheduling

## Validation Contract

Validation must at minimum produce:
- connectivity findings
- type compatibility findings
- bus compatibility findings
- protocol compatibility findings
- carrier policy findings
- loop classification output
- shard-boundary findings
- deterministic validation hash

Evaluation is forbidden unless a network has passed canonical validation under a declared logic network policy.

## Network Policy

Logic network policy declares:
- loop handling
- allowed carrier families
- whether cross-shard links must use boundary artifacts
- whether compiled-only loop relaxation is permitted

Canonical initial policy ids:
- `logic.policy.default`
- `logic.policy.allow_roi_loops`
- `logic.policy.lab_allow`

These network policies compose with, but do not replace, the base LOGIC constitutional policies from LOGIC-0.

## Cross-Shard Rule

Direct synchronous cross-shard wiring is forbidden.

Allowed boundary forms:
- `edge.sig_link`
- explicit boundary artifact exchange declared on the edge or endpoint

See `docs/logic/LOGIC_SHARD_BOUNDARY_RULES.md`.

## Non-Goals for LOGIC-3

- No logic element execution
- No propagation engine
- No oscillation runtime
- No compiled model emission
- No protocol implementation beyond hooks and compatibility declarations
