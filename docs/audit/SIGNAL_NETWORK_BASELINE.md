# SIGNAL_NETWORK_BASELINE

Status: BASELINE
Last Updated: 2026-03-03
Scope: SIG-1 SignalNetworkGraph routing/capacity/delay/loss execution over NetworkGraph.

## 1) Routing and Capacity Model

- Signal transport now uses `NetworkGraph` payload specializations for communication topology:
  - node payload: `signal_node_payload`
  - edge payload: `signal_edge_payload`
- Channel execution is policy-driven via `channel_policy`:
  - routing policy (ABS routing engine)
  - capacity policy
  - delay policy
  - loss policy
  - deterministic budget cost units
- Deterministic ordering guarantees in channel execution:
  - channels ordered by `channel_id`
  - queued envelopes ordered by `envelope_id`
  - route caching keyed by deterministic hash of graph/policy endpoints
- Delay model:
  - effective delay = channel base delay + per-edge delay accumulation
  - envelope progress advances tick-by-tick with deterministic queue carryover when blocked by capacity
- Capacity model:
  - edge-level capacity and channel throughput enforce bounded per-tick advancement
  - overflow remains queued without dropping ordering

## 2) SIG-0 Transport to ABS Routing Integration

- SIG transport no longer uses ad-hoc internal routing.
- Route queries are delegated to ABS routing (`query_route_result`) with deterministic tie-break inherited from ABS.
- Route results are cached in derived state and reused by deterministic cache keying.
- Legacy graph payload compatibility normalization is applied before route queries to avoid schema-shape drift.

## 3) Deterministic Channel Executor

- Added `src/signals/transport/channel_executor.py` for deterministic per-channel processing.
- Per tick behavior:
  - consumes queued envelopes in stable order
  - resolves/reuses route path
  - applies per-hop/per-delivery delay/capacity progression
  - applies policy loss deterministically
- Loss behavior:
  - pure deterministic policies supported (`loss.none`, `loss.linear_attenuation`)
  - named RNG stream policies supported only when explicitly configured (`loss.deterministic_rng`)
- Budget/degrade behavior:
  - bounded processing per channel/tick
  - deterministic defer of remaining envelopes (no silent drops)

## 4) Courier Integration with MOB

- Courier channel support (`sig.policy.courier_basic`) delegates transport to MOB travel.
- Signal envelope is represented as courier commitment metadata and delivered from deterministic courier arrival rows.
- Delivery event/receipt timing aligns with mobility arrival semantics.

## 5) Field Attenuation Hooks (Stub)

- Added deterministic attenuation hook inputs for signal loss modifiers.
- Current implementation supports deterministic modifier tables through queue extension fields.
- Future FIELD-driven attenuation (visibility/radiation/terrain) can attach without refactoring transport contracts.

## 6) UX and Inspection

- Inspection sections integrated:
  - `section.signal.network_summary`
  - `section.signal.channel_queue_depth`
  - `section.signal.delivery_status`
- Overlay integration adds:
  - signal queue heat indication on graph edges
  - queue/delivery summary metadata for entitled inspection contexts

## 7) Enforcement and Test Coverage

- RepoX invariants added:
  - `INV-SIGNALS-USE-ABS-ROUTING`
  - `INV-NO-ADHOC-CAPACITY-LOGIC`
- AuditX analyzers added:
  - `SignalRoutingBypassSmell`
  - `NonDeterministicQueueOrderSmell`
- TestX coverage added/passed:
  - `test_routing_cache_deterministic`
  - `test_capacity_queueing_deterministic`
  - `test_delay_accumulation_deterministic`
  - `test_loss_policy_application_deterministic`
  - `test_courier_channel_delivery_matches_mob_arrival`

## 8) Extension Points

- SIG-4 encryption:
  - channel/execution contracts already carry `encryption_policy_id`; policy depth can increase without altering routing/capacity semantics.
- SIG-5 trust:
  - transport remains content-agnostic; trust/acceptance layers can consume delivery receipts without transport bypass.
- Advanced radio/optical:
  - edge/node payload tags plus channel policy hooks allow attenuation and medium-specific rules while preserving deterministic ordering.

## 9) Gate Runs (2026-03-03)

1. RepoX
- Command: `python tools/xstack/repox/check.py --repo-root . --profile FAST`
- Result: `status=pass` (warn findings only; includes topology declaration warnings resolved by topology regeneration and pre-existing repository warnings).

2. AuditX
- Command: `python tools/xstack/auditx/check.py --repo-root . --profile FAST`
- Result: `status=pass` (scan completed with existing repository warnings).

3. TestX (SIG-1 subset)
- Command: `python tools/xstack/testx/runner.py --repo-root . --profile FAST --cache off --subset testx.signals.routing_cache_deterministic,testx.signals.capacity_queueing_deterministic,testx.signals.delay_accumulation_deterministic,testx.signals.loss_policy_application_deterministic,testx.signals.courier_channel_delivery_matches_mob_arrival`
- Result: `status=pass` (5 selected, 5 passed).

4. strict build
- Command: `python tools/xstack/run.py --repo-root . --skip-testx strict`
- Result: `status=refusal` due pre-existing global strict gate refusals (`compatx` findings, `repox` warning threshold behavior, and packaging lab-build refusal) outside SIG-1 scope; SIG-1 codepaths and targeted TestX suite passed.

5. topology map update
- Command: `python tools/governance/tool_topology_generate.py --repo-root . --out-json docs/audit/TOPOLOGY_MAP.json --out-md docs/audit/TOPOLOGY_MAP.md`
- Result: `complete` (`node_count=2566`, `edge_count=134594`, fingerprint `da01eebff96c294f07c5707c01a333ae164328d2a2c0c97f38e0dcfb44a9917b`).
