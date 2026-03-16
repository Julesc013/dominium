Status: DERIVED
Last Reviewed: 2026-03-16
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: DOC-CONVERGENCE
Replacement Target: canon-aligned documentation set for convergence and release preparation

# LOGIC-9 Distributed Protocol Layer Baseline

## Constitutional Summary

LOGIC-9 makes `ProtocolDefinition` operational without introducing a full general-purpose network stack.

- framed traffic is deterministic and replayable
- arbitration is policy-driven and stable
- addressing remains explicit: unicast, multicast, broadcast
- `carrier.sig` remains SIG-owned for transport, receipts, trust, and encryption
- protocol observation stays instrumentation-gated and compactable

## Framing, Arbitration, And Addressing

Protocol runtime artifacts:

- `schema/logic/protocol_frame.schema`
- `schema/logic/arbitration_state.schema`
- `schema/logic/protocol_event_record.schema`

Protocol registries:

- `data/registries/arbitration_policy_registry.json`
- `data/registries/error_detection_policy_registry.json`
- `data/registries/protocol_registry.json`

Deterministic arbitration modes currently wired:

- `arb.fixed_priority`
- `arb.time_slice`
- `arb.token`

Runtime entry points:

- `src/logic/protocol/protocol_engine.py`
- `src/logic/eval/logic_eval_engine.py`

## SIG Transport Coupling

`carrier.sig` protocol links do not deliver directly to target ports.

- frames are enqueued through `process_signal_send`
- receipt-driven delivery is flushed through `transport_logic_sig_receipts`
- typed payloads survive the SIG transport seam and are reconstructed on receipt
- delivery evidence remains in SIG delivery events and knowledge receipts

Protocol replay/proof tools:

- `tools/logic/tool_replay_protocol_window.py`
- `tools/logic/tool_run_logic_protocol_stress.py`

## Security And Explainability

Protocol links honor `security_policy_id` from the protocol definition.

- failed verification blocks delivery
- explain surfaces include:
  - `explain.protocol_arbitration_loss`
  - `explain.protocol_security_block`
  - `explain.protocol_corruption`

Related shard rule:

- `docs/logic/PROTOCOL_SHARD_RULES.md`

## Debugging Surface

`measure.logic.protocol_frame` now observes framed traffic from protocol frame/event rows rather than only signal metadata.

- protocol sniffing remains instrument-gated
- frame summaries are derived artifacts
- trace capture remains bounded and compactable

## Readiness For LOGIC-10

Ready:

- deterministic framing and arbitration
- SIG-backed distributed delivery seam
- protocol replay and proof chains
- protocol debug/sniffer integration
- cross-shard boundary doctrine

Reserved:

- richer protocol families beyond the current framing/arbitration/addressing hooks
- network-wide routing stacks
- higher-order distributed controller orchestration
