Status: DERIVED
Last Reviewed: unknown
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: DOC-CONVERGENCE
Replacement Target: canon-aligned documentation set for convergence and release preparation

# LOGIC-3 LogicNetworkGraph Baseline

## Constitutional Summary

LOGIC-3 freezes logic topology as a deterministic `NetworkGraph` specialization rather than a bespoke wiring subsystem.

- Nodes are declared as `node.port_in`, `node.port_out`, `node.junction`, `node.bus_junction`, or `node.protocol_endpoint`.
- Edges are declared as `edge.link`, `edge.bus_link`, `edge.protocol_link`, or `edge.sig_link`.
- Payload semantics remain substrate-agnostic. Carrier, delay, noise, and protocol identifiers are policy inputs, not logic semantics.
- Graph creation and mutation are process-mediated through:
  - `process.logic_network_create`
  - `process.logic_network_add_node`
  - `process.logic_network_add_edge`
  - `process.logic_network_remove_edge`
  - `process.logic_network_validate`

## Schemas And Registries

Added LOGIC-3 schema payloads:

- `schema/logic/logic_node_payload.schema`
- `schema/logic/logic_edge_payload.schema`
- `schema/logic/logic_network_binding.schema`

Added LOGIC-3 registries:

- `data/registries/logic_node_kind_registry.json`
- `data/registries/logic_edge_kind_registry.json`
- `data/registries/logic_network_policy_registry.json`

Canonical network policies:

- `logic.policy.default`
  - refuses combinational loops
  - requires explicit boundary handling for cross-shard links
- `logic.policy.allow_roi_loops`
  - marks mixed/combinational loops as `requires_l2_roi`
- `logic.policy.lab_allow`
  - allows loop topologies only when compiled proof is present

## Validation Rules

`src/logic/network/logic_network_validator.py` enforces:

- node kind registration and required port bindings
- edge kind registration and signal/carrier/delay/noise registration
- source/target signal compatibility
- bus definition compatibility for `bus_link`
- protocol compatibility for `protocol_link`
- carrier allow-list enforcement from network policy
- cross-shard boundary refusal unless the link is `sig_link` or an explicit boundary artifact exchange
- deterministic check ordering and validation hashing

## Loop Classification

Cycle classification is deterministic and SCC-based.

- `combinational`
  - cycle contains only combinational element behavior kinds
  - refused by `logic.policy.default`
- `sequential`
  - cycle includes storage/timer/counter behavior
  - allowed under default policy
- `mixed`
  - cycle mixes combinational and sequential behavior kinds
  - policy-gated

Loop outcomes emit or support:

- refusal `refusal.logic.loop_detected`
- explain contract `explain.logic_loop_detected`
- ROI promotion marker `requires_l2_roi`

## Instrumentation And Boundaries

LOGIC-3 binds `logic_network` instrumentation surfaces without exposing omniscient topology truth.

- node observations require declared logic instruments
- edge observations require analyzer-grade access
- whole-network inspection is admin-gated through `control.logic.network.inspect`
- forensics routes through:
  - `forensics.logic.network.loop_detected`
  - `forensics.logic.network.timing_violation`

Cross-shard logic boundary rules are documented in `docs/logic/LOGIC_SHARD_BOUNDARY_RULES.md`.

## Readiness For LOGIC-4

Ready:

- deterministic topology payloads and hashes
- process-mediated topology mutation
- type/protocol/carrier validation
- deterministic loop classification
- L2/compiled escalation markers
- instrumentation-gated network observation

Reserved for LOGIC-4:

- Sense -> Compute -> Commit -> Propagate execution
- canonical propagation ordering across active networks
- per-tick evaluation budgets during execution
- runtime loop handling beyond validation-time classification
