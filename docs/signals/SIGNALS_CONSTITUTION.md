Status: AUTHORITATIVE
Version: 1.0.0
Last Updated: 2026-03-03

# Signals Constitution (SIG-0)

## Purpose

Freeze the canonical communication substrate so every communication flow is represented as:
- information artifact
- deterministic transport over network
- explicit knowledge receipt

This constitution forbids omniscient message teleportation in authoritative truth.

## A) Communication Model

### Artifact
- Message content is an INFO-family artifact referenced by `artifact_id`.
- Transport does not mutate artifact content.

### Transport
- Transport occurs through `signal_channel` over a `network_graph_id`.
- Delivery uses deterministic queueing and route progression.

### Receipt
- Knowledge changes occur through explicit receipt creation (`knowledge_receipt`) per subject.
- Receipt creation is process-mediated and auditable.

## B) Transport Guarantees

### Delay
- Delay is deterministic and derived from channel configuration and routing progress.
- `base_delay_ticks` is channel-defined; all scheduling is tick-based.

### Loss
- Loss is policy-driven via `loss_policy_id`.
- Loss may be deterministic pure function or deterministic named RNG policy.

### Bandwidth
- Bandwidth is `capacity_per_tick` per channel.
- Queue processing is deterministic and budgeted.

## C) Determinism

- Envelope processing order is stable: `channel_id`, then `envelope_id`.
- Delivery/receipt ordering is stable: `artifact_id`, then recipient subject/address order.
- No wall-clock usage in transport, loss, or receipt logic.
- Named RNG streams are permitted only when declared by loss policy and seeded deterministically from artifact/envelope identity + tick.

## D) Epistemics

- Subjects only know artifacts that have produced a receipt for that subject.
- Transport artifacts and delivery events are not equivalent to subject knowledge.
- Admin/truth visibility requires explicit policy/entitlement.

## E) Replay And Proof

- Delivery outcomes are logged as `message_delivery_event` artifacts.
- Receipt creation is logged as process-provenance events.
- Trust metadata changes are logged independently from artifact content.
- Replay must reconstruct transport and receipt outcomes deterministically from event stream + policy registries.

## F) Modding Contract

- Channel types must be declared in `signal_channel_type_registry`.
- Loss policies must be declared in `loss_policy_registry`.
- Encryption policies must be declared in `encryption_policy_registry`.
- Domain packs must extend via registries/schemas only; bespoke hardcoded chat subsystems are forbidden.

## Non-Goals For SIG-0

- No full channel-physics simulation.
- No full trust graph implementation.
- No wall-clock networking model.
- No bypass of control plane, process-only mutation, or epistemic separation.

## Constitutional Invariants

- A1 Determinism is primary.
- A2 Process-only mutation.
- A3 Law-gated authority.
- A7 Observer/Renderer/Truth separation.
- A10 Explicit degradation and refusal.
