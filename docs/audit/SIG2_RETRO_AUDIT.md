Status: AUDIT
Scope: SIG-2 message semantics, addressing, aggregation, and receipt hardening
Date: 2026-03-03

# SIG2 Retro Audit

## Audit Scope
- `src/signals/transport/transport_engine.py`
- `src/signals/transport/channel_executor.py`
- `src/inspection/inspection_engine.py`
- `src/client/interaction/inspection_overlays.py`
- `tools/xstack/repox/check.py`
- `tools/auditx/analyzers/e164_direct_message_smell.py`
- `tools/auditx/analyzers/e165_knowledge_bypass_smell.py`

## Findings

### F1 - Addressing resolution is envelope-local and ad-hoc
- `process_signal_send` currently interprets `recipient_address` inline (`_recipient_rows`) without a dedicated address resolver.
- Group and broadcast handling are represented by generic address map keys and not an explicit address model.
- Impact: Address semantics are not reusable across future dispatch/report/chat-like systems.

### F2 - Queue rows are transport-specific and missing canonical queue entry schema fields
- Transport queue rows exist as derived structures but no dedicated `message_queue_entry` schema contract.
- `scheduled_tick` and explicit `next_hop_node_id` are not first-class canonical fields.
- Impact: replay/debug contracts are weaker and adapters can drift.

### F3 - Artifact validation at send path is minimal
- `process_signal_send` validates channel and envelope shape but does not enforce artifact catalog existence/family metadata.
- Impact: ad-hoc artifact IDs can be transported without explicit INFO-family grounding.

### F4 - Receipt idempotency is envelope/tick-centric, not subject/artifact-centric
- Receipt creation currently derives `receipt_id` with `acquired_tick` and can create repeated semantic acquisitions when duplicate deliveries occur.
- Impact: at-least-once delivery semantics can overcount knowledge acquisition effects unless downstream code filters duplicates.

### F5 - Aggregation semantics are absent
- No deterministic aggregation engine exists for report batching over INFO artifacts.
- Existing report-like outputs are domain-specific and not routed through signal dispatch semantics.
- Impact: future institutional reporting risks bespoke implementations.

### F6 - Inspection lacks explicit inbox/sent/aggregation sections
- SIG-1 added network and queue depth sections but not recipient-facing message inbox/sent status and aggregation status views.
- Impact: operational visibility remains transport-centric rather than message semantics-centric.

## Direct Broadcast / Direct Knowledge Mutation Audit
- No direct mutation of `knowledge_receipts` found outside signal transport helper path in core signal sources.
- Existing AuditX analyzers (`E164`, `E165`) already flag direct bypass classes, but SIG-2 requires targeted broadcast bypass and direct knowledge mutation analyzers.

## Migration Plan
1. Add canonical SIG-2 schemas for address, queue entry, and aggregation policy.
2. Add addressing and aggregation registries; wire into CompatX version registry.
3. Introduce deterministic address resolution engine (`src/signals/addressing/address_engine.py`).
4. Update `process_signal_send` to validate artifacts, resolve addresses, and emit deterministic queue entries.
5. Make receipt acquisition idempotent by subject/artifact while preserving delivery event log.
6. Add aggregation engine that produces REPORT artifacts and dispatches through normal signal send path.
7. Add inspection sections for inbox/sent/aggregation views.
8. Add RepoX and AuditX enforcement for direct artifact delivery and broadcast bypass.
9. Add deterministic TestX coverage for resolution/order/idempotency/aggregation/no-bypass.
