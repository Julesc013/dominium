Status: DERIVED
Version: 1.0.0
Last Reviewed: 2026-02-16
Compatibility: Bound to `data/registries/server_profile_registry.json`, `data/registries/securex_policy_registry.json`, `tools/xstack/sessionx/net_handshake.py`, and refusal contract.

# Ranked Server Governance Baseline

## Scope
MP-8 baseline for policy-driven ranked/casual/private multiplayer governance with deterministic SecureX + anti-cheat enforcement.

## Server Profile Matrix

1. `server.profile.rank_strict`
   - `securex_policy_id`: `securex.policy.rank_strict`
   - `anti_cheat_policy_id`: `policy.ac.rank_strict`
   - allowed replication policies: lockstep + server-authoritative
   - observer-style law profile requests refused unless explicitly allowed by profile
2. `server.profile.casual_public`
   - `securex_policy_id`: `securex.policy.casual_default`
   - `anti_cheat_policy_id`: `policy.ac.casual_default`
   - broader policy set, warning-oriented trust posture
3. `server.profile.private_relaxed`
   - `securex_policy_id`: `securex.policy.private_relaxed`
   - `anti_cheat_policy_id`: `policy.ac.private_relaxed`
   - unsigned content may be accepted by explicit policy

## SecureX Enforcement Summary

1. Handshake validates:
   - pack lock hash + registry hashes + schema versions
   - server profile policy constraints
   - SecureX signature posture against resolved lockfile packs
2. Ranked strict refusal codes:
   - `refusal.net.handshake_securex_denied`
   - `refusal.net.handshake_policy_not_allowed`
3. Legacy server policy compatibility is preserved through deterministic fallback profile synthesis.

## Proof Artifact Structure

`tools/net/tool_export_ranked_proof_bundle.py` exports:

1. JSON bundle:
   - handshake request/response transcript
   - pack signature table from lockfile
   - registry hash table
   - hash anchor frames (if provided)
   - anti-cheat events/actions (if provided)
   - deterministic provenance + content hash
2. Markdown summary:
   - canonical IDs/hashes
   - source artifact paths
   - counts for signatures/anchors/events/actions

## Test Coverage (MP-8)

1. `testx.net.ranked_refuse_unsigned_pack`
2. `testx.net.private_accept_unsigned_pack`
3. `testx.net.ranked_refuse_observer_law`
4. `testx.net.ranked_requires_ac_rank_strict`
5. `testx.net.ranked_proof_bundle_generated`

## Guardrails

1. RepoX invariants:
   - `INV-RANKED-REQUIRES-SECUREX-STRICT`
   - `INV-NO-RANKED-FLAGS`
2. AuditX analyzers:
   - `E11_RANKED_POLICY_DRIFT`
   - `E12_SIGNATURE_BYPASS_SMELL`

## Extension Points

1. Replace SecureX `status_only_stub` verification mode with cryptographic signature chain verification.
2. Add tournament-specific proof packaging metadata (event IDs, bracket context).
3. Add third-party attestation bridge as an optional policy module (no implicit dependency).
