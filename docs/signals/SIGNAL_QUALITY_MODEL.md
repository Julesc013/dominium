Status: AUTHORITATIVE
Version: 1.0.0
Last Updated: 2026-03-03

# Signal Quality Model (SIG-3)

## Purpose
Define deterministic attenuation, noise, interference, and jamming behavior for SIG transport without introducing non-replayable RF simulation.

## A) Attenuation

- Attenuation is policy-driven and evaluated per message hop/delivery attempt.
- Inputs:
  - channel/loss policy parameters
  - per-edge/path attenuation modifiers
  - optional deterministic FIELD modifiers
- Each evaluation yields a deterministic quality score or threshold.

Field integration rules:
- FIELD sampling inputs are derived-only and cached by `(tick, graph_id, node_id|edge_id, field_type_id)`.
- Missing field data resolves to deterministic neutral defaults.

## B) Noise Model

Deterministic noise function:
- `f(envelope_hash, hop_index, tick, policy_parameters, channel_id)`

RNG policy:
- Named RNG is only allowed when `loss_policy.uses_rng_stream = true`.
- Stream identity must be explicit (`rng_stream_name`).
- Seed/materialization derives from deterministic tuple:
  - `(rng_stream_name, envelope_id, hop_index, tick, channel_id)`.

No wall-clock entropy is allowed.

## C) Corruption Model

- Artifact payload is never mutated in place by transport.
- Corruption is represented transport-side:
  - `delivery_state = corrupted`
  - optional `corrupted_view = true` metadata in delivery event extensions.
- Canonical artifact remains unchanged; epistemic consumers may render degraded interpretation from delivery metadata.

Invariant:
- No silent corruption. Every corruption outcome must emit a delivery event and provenance-compatible metadata.

## D) Jamming and Interference

- Jamming is modeled as deterministic effect state attached to channel or channel endpoint.
- Jamming influences effective attenuation/noise and may force `lost` when policy threshold is exceeded.
- Jamming must be process-triggered:
  - `process.signal_jam_start`
  - `process.signal_jam_stop`
- All start/stop and impact outcomes are logged through decision/provenance paths.

## Determinism and Ordering

- Channels are processed in `channel_id` order.
- Queue entries are processed in deterministic queue key order.
- Quality evaluations are deterministic for identical inputs.
- Budget degradation processes first `N` eligible queue entries per channel deterministically.

## Delivery States

Transport quality outcomes are limited to:
- `delivered`
- `lost`
- `corrupted`

Each outcome is explicit in `message_delivery_event.delivery_state`.

## Integration Contracts

- SIG-0/1/2: quality extends existing transport path and receipt semantics.
- FIELD-1: deterministic field hooks for attenuation modifiers.
- CTRL: named RNG policy enforcement and decision logging.
- MAT: delivery quality outcomes remain event-sourced and replayable.

## Non-Goals (SIG-3)

- Real RF or electromagnetic propagation simulation.
- Wall-clock or platform-entropy driven quality outcomes.
- Encryption/auth content transforms (SIG-4).
- Trust graph acceptance logic (SIG-5).
