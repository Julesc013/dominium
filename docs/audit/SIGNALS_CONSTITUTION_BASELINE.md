Status: Baseline implemented for SIG-0 (signals + communication constitution).
Date: 2026-03-03
Stability: provisional
Future Series: DOC-ARCHIVE
Replacement Target: legacy reference surface retained without current binding authority

# SIG-0 Signals Constitution Baseline

## Transport Model

- Canonical communication chain:
  - INFO artifact (`artifact_id`)
  - transport envelope (`signal_message_envelope`)
  - delivery event (`message_delivery_event`)
  - epistemic receipt (`knowledge_receipt`)
- Deterministic transport skeleton implemented in `src/signals/transport/transport_engine.py`:
  - `process_signal_send(...)` helper
  - `process_signal_transport_tick(...)` helper
  - `process_knowledge_acquire(...)` helper
- Channel model is registry and schema driven:
  - `signal_channel` with `capacity_per_tick`, `base_delay_ticks`, `loss_policy_id`, `encryption_policy_id`
  - channel types in `data/registries/signal_channel_type_registry.json`
  - loss policies in `data/registries/loss_policy_registry.json`
  - encryption policies in `data/registries/encryption_policy_registry.json`

## Determinism Guarantees

- Queue and delivery processing are deterministic:
  - stable ordering by channel/envelope/recipient queue key
  - deterministic event and receipt IDs via canonical hash
- Delay/bandwidth are tick-based and deterministic.
- Loss policies:
  - `loss.none`
  - `loss.linear_attenuation`
  - `loss.deterministic_rng` with named stream and deterministic hash roll
- No wall-clock APIs in SIG transport path.

## Artifact And Epistemic Separation

- Artifact content is never rewritten by transport.
- Delivery events represent transport outcome only.
- Knowledge is represented only by receipt rows created on successful delivery.
- Trust hook integrated:
  - `knowledge_receipt.trust_weight` (default `1.0`)
  - subject trust override map accepted by transport tick helper
  - trust affects downstream acceptance later; content remains unchanged.

## Enforcement

- RepoX scaffolding added:
  - `INV-NO-DIRECT-KNOWLEDGE-TRANSFER`
  - `INV-SIGNAL-TRANSPORT-ONLY`
- AuditX analyzers added:
  - `E164_DIRECT_MESSAGE_SMELL` (`DirectMessageSmell`)
  - `E165_KNOWLEDGE_BYPASS_SMELL` (`KnowledgeBypassSmell`)

## TestX Coverage

- Added:
  - `test_message_delivery_deterministic`
  - `test_loss_policy_deterministic`
  - `test_receipt_created_only_on_delivery`
  - `test_no_direct_knowledge_mutation`
- Result:
  - subset pass (4/4) in deterministic TestX run.

## Extension Plan (SIG-1..SIG-7)

- SIG-1: route-aware multi-hop channel traversal and richer bandwidth arbitration.
- SIG-2: delivery classes/QoS and bounded retry semantics.
- SIG-3: encryption semantics beyond deterministic stub.
- SIG-4/5: trust graph and acceptance policy integration.
- SIG-6: shard-aware channel federation with deterministic cross-shard transport.
- SIG-7: comms institutions/automation overlays while preserving process-only mutation.

## Gate Run Summary

Executed on 2026-03-03:

1. RepoX
- Command: `python tools/xstack/repox/check.py --repo-root . --profile FAST`
- Result: `status=pass` (warn findings only; includes pre-existing repository warnings and SIG runtime hook reminder warning).

2. AuditX
- Command: `python tools/xstack/auditx/check.py --repo-root . --profile FAST`
- Result: `status=pass` (warnings/findings reported by policy).

3. TestX
- Command: `python tools/xstack/testx/runner.py --repo-root . --profile FAST --cache off --subset testx.signals.message_delivery_deterministic,testx.signals.loss_policy_deterministic,testx.signals.receipt_created_only_on_delivery,testx.signals.no_direct_knowledge_mutation`
- Result: `status=pass` (4 selected, 4 passed).

4. Strict build
- Command: `python tools/xstack/run.py --repo-root . --skip-testx strict`
- Result: global `result=refusal` due existing non-SIG strict gates (`compatx` findings and packaging lab-build refusal); SIG-related strict steps passed (`registry compile`, `repox`, `auditx`).

5. Topology map
- Command: `python tools/governance/tool_topology_generate.py --repo-root . --out-json docs/audit/TOPOLOGY_MAP.json --out-md docs/audit/TOPOLOGY_MAP.md`
- Result: `complete` with deterministic fingerprint `95f814405c4b26ba055e90b0fb433d647f6592151f837f3228b6385cfdc83993`.
