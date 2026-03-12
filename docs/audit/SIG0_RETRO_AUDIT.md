Status: AUDIT
Scope: SIG-0 signals and communication constitution retrofit
Date: 2026-03-03
Stability: provisional
Future Series: DOC-CONVERGENCE
Replacement Target: canon-aligned documentation set for convergence and release preparation

# SIG0 Retro Audit

## Audit Method
- Scanned authoritative process/runtime paths in `tools/xstack/sessionx/process_runtime.py` for communication and knowledge mutation patterns.
- Scanned epistemic/memory paths:
  - `src/epistemics/memory/memory_kernel.py`
- Scanned net/SRZ paths for shard transfer patterns:
  - `src/net/srz/*`
  - `src/net/transport/*`

## Findings

### F1 - Direct message insertion bypasses transport channel model
- Existing:
  - `process.instrument_radio_send_text` writes directly to `instrument.radio_text.state.inbox`.
  - Message rows are created and marked as effectively delivered in the same process tick.
- Gap against SIG constitution:
  - No explicit `signal_channel` artifact for this flow.
  - No deterministic delay/loss/bandwidth policy is applied.
  - Receipt acquisition is implicit via inbox mutation, not explicit receipt process.

### F2 - Communication and epistemic receipt are conflated
- Existing:
  - Radio process writes directly to instrument state/output channels.
  - Memory consumption reads diegetic channels, but there is no canonical transport `delivery_event -> knowledge_receipt` chain.
- Gap against SIG constitution:
  - Artifact transport and receipt are not separated as first-class deterministic artifacts.

### F3 - Omniscient debug broadcast path not found in authoritative process runtime
- Existing:
  - No obvious global "broadcast all subjects" direct path in authoritative runtime process handlers.
- Note:
  - This audit is scoped to current process/runtime and known communication surfaces; future checks should keep scanning control adapters and debug tools.

### F4 - Direct shard-to-shard truth sharing bypass for communication was not identified in current SRZ transport stubs
- Existing:
  - SRZ/net code paths are envelope-oriented and policy-driven.
- Gap:
  - Signals communication substrate is currently separate and not integrated with these transport contracts.

## Migration Plan
1. Introduce canonical SIG artifacts:
- `signal_channel`
- `signal_message_envelope`
- `message_delivery_event`
- `knowledge_receipt` acquisition process hook

2. Add deterministic transport skeleton:
- `process.signal_send`
- `process.signal_transport_tick`
- deterministic ordering by `envelope_id` and channel
- deterministic delay/loss/bandwidth enforcement

3. Add explicit receipt process:
- `process.knowledge_acquire` for receipt creation only on delivered events
- trust metadata hook (`trust_weight`) attached at receipt

4. Deprecate direct-delivery radio path over time:
- keep current diegetic radio semantics operational for compatibility
- route future communication actions through SIG transport queue + receipt path
- preserve replay/provenance continuity during migration

5. Add enforcement:
- RepoX invariant checks for direct knowledge bypass and non-transport signal mutation
- AuditX smells for direct message injection and knowledge bypass writes
