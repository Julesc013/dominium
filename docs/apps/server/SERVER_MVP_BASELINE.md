Status: CANONICAL
Last Reviewed: 2026-03-10
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: DOC-CONVERGENCE
Replacement Target: canon-aligned documentation set for convergence and release preparation

# SERVER MVP Baseline

## Purpose

SERVER-MVP-0 defines the v0.0.0 headless authoritative runtime surface.

It provides:

- deterministic session boot
- contract, pack, mod, and overlay validation
- loopback client connect
- authority-gated intent submission
- deterministic simulation tick advancement
- periodic replay-anchor emission

It does not provide:

- matchmaking
- external persistence services
- anti-cheat beyond existing contract/policy enforcement
- a full replication protocol

## Responsibilities

The v0.0.0 server is responsible for:

- loading a pinned `SessionSpec`
- validating:
  - `universe_contract_bundle_hash`
  - `semantic_contract_registry_hash`
  - `pack_lock_hash`
  - `mod_policy_id`
  - `overlay_conflict_policy_id`
- running authoritative TruthModel ticks
- enforcing `AuthorityContext` for all client intents
- emitting replay anchors and proof bundles
- exposing deterministic operator commands through CLI-only stubs

## Connection Model

The MVP transport is deterministic in-process loopback.

- client connects through `transport.loopback`
- server accepts connections in stable `connection_id` order
- each accepted connection is assigned:
  - `connection_id`
  - `peer_id`
  - `account_id` stub
  - `AuthorityContext`
  - entitlements derived from the active server profile/policy

The authoritative server remains the source of truth.
Clients receive session info and tick-stream stubs only.

## Deterministic Tick

- simulation time advances only through canonical ticks
- wall-clock is forbidden for authoritative scheduling
- server runtime may be run in:
  - single-step mode
  - run-`N`-ticks mode
- proof anchors are emitted every configured `proof_anchor_interval_ticks`

## Proof Anchors

Each emitted proof anchor includes:

- `tick`
- `pack_lock_hash`
- `contract_bundle_hash`
- `semantic_contract_registry_hash`
- `mod_policy_id`
- `overlay_manifest_hash`
- `hash_anchor_frame`
- `tick_hash`
- `control_proof_hash`

Proof anchors are deterministic derived artifacts.

## Authority Enforcement

Every incoming client intent must be wrapped in `AuthorityContext`.

- missing authority context: refuse
- mismatched connection authority: refuse
- law-forbidden intent: refuse through existing process/law path

Server operators may inspect or kick connections through CLI-only commands, but
must not mutate authoritative truth outside process execution.

## Refusal Codes

- `refusal.session.contract_mismatch`
- `refusal.session.pack_lock_mismatch`
- `refusal.client.unauthorized`

Additional lower-level refusal codes from CompatX, mod policy, or law/process
execution remain valid and may be surfaced as the detailed cause.
