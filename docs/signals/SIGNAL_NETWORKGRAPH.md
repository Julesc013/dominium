Status: AUTHORITATIVE
Version: 1.0.0
Last Updated: 2026-03-03
Stability: provisional
Future Series: DOC-CONVERGENCE
Replacement Target: patched document aligned to current canon ownership and release scope

# Signal NetworkGraph Model (SIG-1)

## Patch Notes

- Current status: partially aligned to the Constitutional Architecture and release-freeze documentation set.
- Required updates: documentation surface exists, but current canon ownership is not explicit
- Cross-check with: `docs/audit/CANON_MAP.md` and `docs/audit/DOC_DRIFT_MATRIX.md`.


## Purpose
Define deterministic signal transport as NetworkGraph flow execution with explicit routing, capacity, delay, and loss policies.

## SignalNetworkGraph
SignalNetworkGraph is a NetworkGraph specialization with signal payload types:
- `signal_node_payload`
- `signal_edge_payload`

Signal channels bind to a specific graph and policy set.

## Payload Types

### signal_node payload
`node_kind` values:
- `exchange`
- `tower`
- `router`
- `station`
- `antenna`
- `relay`

### signal_edge payload
`edge_kind` values:
- `wire`
- `fiber`
- `relay_link`
- `broadcast_link`
- `courier_link`

Edge payload carries deterministic execution inputs:
- `capacity_per_tick`
- `delay_ticks`
- optional `loss_modifier`

## Channel Binding
Each channel references:
- `network_graph_id`
- `channel_policy_id`
- `loss_policy_id` (resolved by policy)

Policy controls:
- routing policy id (ABS)
- capacity policy
- delay policy
- loss policy
- budget cost units

## Routing Contract
Routing MUST use ABS deterministic route engine:
- `query_route_result(graph_row, routing_policy_row, from_node_id, to_node_id, ...)`
- deterministic tie-break remains delegated to ABS.

Route cache key must include:
- graph hash
- from node
- to node
- routing policy id
- constraints hash

## Deterministic Capacity Enforcement
Per tick:
1. Process channels sorted by `channel_id`.
2. Process queued envelopes sorted by `envelope_id` and queue key.
3. Apply per-channel capacity.
4. Apply per-edge capacity along routed hop.
5. If capacity is exhausted, keep envelope queued (no silent drop).

## Deterministic Delay Model
Delivery delay is:
- `channel.base_delay_ticks`
- plus sum of routed edge `delay_ticks`

Envelope progression is tick-based only. No wall-clock inputs are allowed.

## Loss Model
Loss policy is deterministic and policy-driven:
- pure deterministic function, or
- named RNG stream policy with deterministic seed components.

Allowed deterministic seed components:
- envelope identity hash
- hop index
- simulation tick

## Budget/Degradation
Channel execution is budgeted by cost units.
Deterministic degradation rule:
- process first `N` envelopes per channel (stable order),
- defer remainder without mutation.

All degradation outcomes must be loggable and replayable.

## Channel Type Notes
- `channel.wired_basic`: edge-constrained graph route.
- `channel.radio_basic`: graph route with policy attenuation hooks.
- `channel.optical_line_of_sight`: graph-based stub with future geometry LoS adapter.
- `channel.courier_route`: delegates transport to MOB itinerary/arrival events.

## Replay Contract
Replay determinism requires:
- stable ordering by `channel_id` then `envelope_id`,
- deterministic route cache keys,
- deterministic delivery/loss events,
- explicit receipt creation only after delivered state.
