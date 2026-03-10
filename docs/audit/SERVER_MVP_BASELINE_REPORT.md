Status: DERIVED
Last Reviewed: 2026-03-10
Supersedes: none
Superseded By: none

# SERVER MVP Baseline Report

## Boot Validation Matrix

SERVER-MVP-0 validates the following before authoritative runtime start:

- `universe_contract_bundle_hash`
- `semantic_contract_registry_hash`
- `pack_lock_hash`
- `mod_policy_id`
- `overlay_conflict_policy_id`
- `server_config_id`

Stable refusal codes:

- `refusal.session.contract_mismatch`
- `refusal.session.pack_lock_mismatch`
- `refusal.client.unauthorized`

## Connection Protocol Summary

The MVP connection surface is deterministic loopback only.

- client sends `handshake_request`
- server assigns deterministic `connection_id`
- server creates `AuthorityContext`
- server returns `handshake_response`
- server may stream `server.tick_stream.stub.v1` payloads after acceptance

No full replication protocol is included in v0.0.0.

## Proof Anchor Format

Every emitted proof anchor includes:

- `tick`
- `pack_lock_hash`
- `contract_bundle_hash`
- `semantic_contract_registry_hash`
- `mod_policy_id`
- `overlay_manifest_hash`
- `tick_hash`
- `hash_anchor_frame`
- `control_proof_hash`

Proof anchors are derived, deterministic, and replay-verifiable.

## Operational Surface

Minimal CLI server commands are present:

- `server status`
- `list clients`
- `kick client` stub
- `save snapshot`
- `emit diag bundle` stub

These commands must not mutate authoritative truth outside process execution.

## Readiness

SERVER-MVP-0 is ready for:

- SERVER-MVP-1 local supervisor and client-spawn integration
- APPSHELL command-hosting work
- deterministic replay-anchor collection for long-lived server sessions

Known intentional limitations:

- loopback transport only
- no external persistence service
- no matchmaking
- no anti-cheat beyond existing contract/policy enforcement
