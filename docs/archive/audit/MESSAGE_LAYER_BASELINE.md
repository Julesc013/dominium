Status: DERIVED
Last Reviewed: 2026-03-16
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: DOC-CONVERGENCE
Replacement Target: canon-aligned documentation set for convergence and release preparation

# MESSAGE_LAYER_BASELINE

Status: BASELINE
Last Updated: 2026-03-03
Scope: SIG-2 message artifact semantics, addressing, aggregation, and receipt behavior.

## 1) Artifact/Envelope Separation

- Message content remains INFO-family artifact (`artifact_id`, `artifact_family_id`) and is never mutated by transport.
- Transport metadata remains envelope-scoped (`signal_message_envelope`).
- `process_signal_send` now validates artifact references deterministically:
  - `artifact_id` required
  - if artifact catalog rows are provided, artifact existence is required
  - artifact family presence is required when catalog validation is active

## 2) Addressing Semantics

Implemented deterministic addressing engine:
- `src/signals/addressing/address_engine.py`

Supported modes:
- `subject` (unicast)
- `group` (multicast)
- `broadcast` (scope-based)

Contracts:
- recipient resolution sorted by `subject_id`
- deterministic fallback for inline group/broadcast targets
- no implicit global omniscient broadcast path

## 3) Queue and Dispatch Semantics

`process_signal_send` now executes deterministic dispatch pipeline:
1. validate channel and artifact contract
2. resolve address via address engine
3. create canonical queue entries
4. enqueue by deterministic ordering
5. emit decision-log entry payload

Queue semantics:
- canonical queue entry id via deterministic hash
- queue row includes `queue_entry_id`, `next_hop_node_id`, `scheduled_tick`
- ordering key effectively preserves envelope then subject ordering

## 4) Delivery and Receipt Semantics

Receipt path:
- delivery event -> `process_knowledge_acquire` -> `knowledge_receipt`

Idempotency:
- receipts are idempotent by `subject_id + artifact_id`
- duplicate deliveries for same subject/artifact do not create duplicate semantic acquisition rows

Receipt fields now include:
- `trust_weight`
- `verification_state` (`unverified|verified|disputed`)

## 5) Aggregation Model

Implemented deterministic aggregation engine:
- `src/signals/aggregation/aggregation_engine.py`

Capabilities:
- scheduled aggregation policy execution
- deterministic selection of eligible artifacts by family + tick window
- deterministic summary strategies (`count_by_family`, `latest_by_subject`, `disabled`)
- REPORT artifact creation with deterministic IDs/fingerprints
- dispatch through normal signal send path (no bypass)

## 6) UX and Inspection Integration

Added inspection sections:
- `section.signal.inbox_summary`
- `section.signal.sent_messages`
- `section.signal.aggregation_status`

These sections expose message-layer state from receipts/envelopes/aggregation artifacts with existing epistemic gating.

## 7) Enforcement Additions

RepoX:
- `INV-NO-DIRECT-ARTIFACT-DELIVERY`
- `INV-RECEIPT-REQUIRED-FOR-KNOWLEDGE`

AuditX:
- `DirectKnowledgeMutationSmell` (`E168`)
- `BroadcastBypassSmell` (`E169`)

## 8) TestX Coverage (SIG-2)

Added and passing:
1. `testx.signals.address_resolution_deterministic`
2. `testx.signals.queue_order_deterministic`
3. `testx.signals.receipt_idempotent`
4. `testx.signals.aggregation_deterministic`
5. `testx.signals.no_direct_delivery`

## 9) Gate Runs (2026-03-03)

1. RepoX
- Command: `python tools/xstack/repox/check.py --repo-root . --profile FAST`
- Result: `status=pass` (warn findings only; pre-existing repository warnings remain)

2. AuditX
- Command: `python tools/xstack/auditx/check.py --repo-root . --profile FAST`
- Result: `status=pass` (scan executed; existing warnings reported)

3. TestX (SIG-2 subset)
- Command: `python tools/xstack/testx/runner.py --repo-root . --profile FAST --cache off --subset testx.signals.address_resolution_deterministic,testx.signals.queue_order_deterministic,testx.signals.receipt_idempotent,testx.signals.aggregation_deterministic,testx.signals.no_direct_delivery`
- Result: `status=pass` (5 selected, 5 passed)

4. strict build
- Command: `python tools/xstack/run.py --repo-root . --skip-testx strict`
- Result: `status=refusal` due pre-existing global strict gate failures outside SIG-2 scope (`compatx` findings and packaging lab-build refusal)

5. topology map update
- Command: `python tools/governance/tool_topology_generate.py --repo-root . --out-json docs/audit/TOPOLOGY_MAP.json --out-md docs/audit/TOPOLOGY_MAP.md`
- Result: `complete` (`node_count=2585`, `edge_count=140438`, fingerprint `b23bedc5c6de7720df71ab987ef468c86d315ef21b775e01280266b6967e81e2`)

## 10) Extension Notes

- SIG-4 (encryption/auth):
  - message queue/envelope semantics remain compatible with policy-based encryption overlays.
- SIG-5 (trust graph):
  - receipt `trust_weight` and `verification_state` provide stable input hooks.
- Future institutional dispatch:
  - aggregation and addressing remain policy/registry-driven and deterministic.
