Status: DERIVED
Last Reviewed: 2026-03-16
Supersedes: none
Superseded By: none
Scope: SIG-1 SignalNetworkGraph routing/capacity/delay retrofit
Date: 2026-03-03
Stability: provisional
Future Series: DOC-CONVERGENCE
Replacement Target: canon-aligned documentation set for convergence and release preparation

# SIG1 Retro Audit

## Audit Scope
- `src/signals/transport/transport_engine.py`
- `src/core/graph/routing_engine.py`
- `tools/xstack/sessionx/process_runtime.py`
- `tools/xstack/repox/check.py`

## Findings

### F1 - SIG-0 transport bypasses ABS routing
- Current `tick_signal_transport` checks only direct edge adjacency (`_has_direct_route`).
- No deterministic multi-hop path query through `query_route_result(...)`.
- Impact: routing semantics diverge from canonical NetworkGraph routing policy.

### F2 - Capacity handling is channel-local only
- Current capacity gating is only `channel.capacity_per_tick`.
- No per-edge capacity accounting while traversing route edges.
- Impact: channel flow can violate edge-level bandwidth assumptions.

### F3 - Delay model is queue-local only
- Current queue rows only decrement `remaining_delay_ticks` from channel base delay.
- No per-edge delay accumulation from routed path.
- Impact: deterministic timing does not reflect graph path cost.

### F4 - Channel execution logic is embedded inside transport engine
- Routing, delay, loss, and delivery decisions are in a single loop.
- No channel executor boundary for deterministic budgeted path progression.
- Impact: hard to enforce shared capacity rules and future channel policies.

### F5 - Process runtime has no explicit SIG process handlers
- `process.signal_send`, `process.signal_transport_tick`, and `process.knowledge_acquire` are not surfaced as runtime process branches.
- SIG helpers exist, but runtime dispatch does not expose canonical process entrypoints.

## Ad-hoc Routing/Channel Special Cases
- Wired/radio/courier/optical are represented as channel types in registry.
- Execution path in SIG-0 does not yet branch by policy in a reusable `channel_policy` layer.
- Courier travel binding to MOB commitments is not yet wired.

## Migration Plan
1. Introduce signal graph payload schemas and channel policy schema.
2. Add signal channel policy and node/edge kind registries.
3. Add deterministic `channel_executor` that:
   - queries routes through ABS,
   - caches route results by graph hash/from/to/policy,
   - enforces per-channel and per-edge capacity,
   - accumulates channel + edge delay deterministically,
   - applies deterministic loss policy.
4. Route SIG transport tick through the new executor.
5. Add courier-channel handoff to MOB travel artifacts as deterministic stub.
6. Add field attenuation hook point for policy-derived loss modifiers.
7. Add enforcement and tests for:
   - ABS routing usage,
   - deterministic queue ordering,
   - deterministic delay/capacity/loss behavior.
