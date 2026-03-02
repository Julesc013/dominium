Status: AUTHORITATIVE
Version: 1.0.0
Last Updated: 2026-03-03

# Message Semantics (SIG-2)

## Purpose
Define canonical message-layer semantics for artifacts, addressing, queueing, aggregation, and receipts so communication remains deterministic, replayable, and non-bespoke.

## A) Artifact vs Envelope

- Artifact:
  - INFO-family content object (observation, record, report, etc.).
  - Immutable in transport path.
  - Canonical identifier: `artifact_id`.
- Envelope:
  - Transport metadata wrapper carrying sender/address/channel references.
  - Contains no authority to mutate artifact semantics.
  - Canonical identifier: `envelope_id`.

Invariant:
- Transport may delay/loss/defer envelopes, but must never mutate artifact payload meaning.

## B) Addressing Modes

Message addresses are canonical and typed:

- `subject` (unicast)
  - `target_id` is a single `subject_id`.
- `group` (multicast)
  - `target_id` is `group_id`; resolver maps group to deterministic subject set.
- `broadcast` (graph-scoped)
  - `target_id` is `broadcast_scope_id`; resolver maps scope to deterministic subject set.

Resolver contract:
- Recipient list must be sorted lexicographically by `subject_id`.
- Empty resolution is explicit and inspectable.
- No implicit global omniscient broadcast.

## C) Delivery Guarantees

Default guarantee:
- at-least-once delivery attempts through deterministic queue execution.

Optional idempotency:
- knowledge effects are idempotent by `subject_id + artifact_id`.
- duplicate delivered envelopes for same subject/artifact do not produce duplicate semantic acquisition.

Transport constraints:
- deterministic ordering by channel/envelope/recipient.
- deterministic capacity and delay from channel + graph policies.
- deterministic loss policy (pure function or named RNG stream when declared).

## D) Receipts

Receipts are created only on successful delivery:

- receipt fields include:
  - `subject_id`
  - `artifact_id`
  - `envelope_id`
  - `trust_weight`
  - `verification_state`
  - deterministic fingerprint
- Receipt creation path is process-mediated (`process.knowledge_acquire`).
- Knowledge must not be acquired without receipt creation.

## E) Aggregation

Aggregation produces REPORT artifacts from lower-level artifact families.

- Input artifacts selected by deterministic policy (`aggregation_policy`).
- Execution is schedule-driven (tick-based, no wall-clock).
- Summarization rules must be deterministic and inspectable.
- Output REPORT artifacts must be dispatched through standard signal send path.

Examples:
- `agg.daily_summary`
- `agg.incident_batch`
- `agg.none` (disabled/no-op policy)

## Determinism and Replay

- Queue ordering key: `(channel_id, envelope_id, recipient_subject_id, queue_entry_id)`.
- Address resolution output ordering: sorted `subject_id`.
- Aggregation input ordering: `(artifact_tick, artifact_id)`.
- Delivery and receipt events are event-sourced for reenactment.

## Non-Goals (SIG-2)

- No encryption/authentication semantics (SIG-4).
- No full trust graph/influence graph (SIG-5).
- No wall-clock time integration.

## Integration Notes

- CTRL: DecisionLog records send/deferral/aggregation decisions.
- MAT: Delivery and receipt events remain provenance-linked.
- ABS: Routing/capacity/delay remain transport-layer concerns from SIG-1.
- META-INFO: Artifact family semantics remain source of content meaning.
