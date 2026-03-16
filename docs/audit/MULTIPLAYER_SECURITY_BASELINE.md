Status: DERIVED
Last Reviewed: 2026-03-16
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: DOC-CONVERGENCE
Replacement Target: canon-aligned documentation set for convergence and release preparation

# Multiplayer Security Baseline

Status: DERIVED BASELINE  
Last Updated: 2026-02-16

## Governance Inputs
Security behavior is fully policy-driven by:

- `server_profile_id`
- `securex_policy_id`
- `anti_cheat_policy_id`
- `replication_policy_id`
- `law_profile_id`

No runtime `*_mode` flags are allowed.

## Ranked Acceptance/Refusal Matrix
Ranked governance (`server.profile.rank_strict`) requires:

- `securex.policy.rank_strict`
- `policy.ac.rank_strict`
- allowed replication policy from server profile registry
- allowed law profile from server profile registry
- signed/official pack posture according to SecureX policy

Deterministic refusals include:

- `refusal.net.handshake_pack_lock_mismatch`
- `refusal.net.handshake_registry_hash_mismatch`
- `refusal.net.handshake_schema_version_mismatch`
- `refusal.net.handshake_policy_not_allowed`
- `refusal.net.handshake_securex_denied`
- `refusal.net.authority_violation`

## Anti-Cheat Expectations
Server-side anti-cheat engine must produce deterministic:

- `anti_cheat_event` rows
- enforcement action rows
- refusal injection rows
- anchor mismatch rows

Policy expectations:

- `policy.ac.detect_only`: event emission only; no forced refusal/terminate.
- `policy.ac.casual_default`: targeted refusal/throttle, no implicit terminate escalation.
- `policy.ac.rank_strict`: deterministic escalation including refusal/terminate where configured.
- `policy.ac.private_relaxed`: minimal checks and audit-first behavior.

## Evidence Artifacts
Ranked and strict verification runs must generate:

- handshake transcript artifacts
- lockfile hash + registry hash table
- per-tick/composite hash anchors
- anti-cheat event and enforcement logs
- refusal audit trail

Artifacts are canonical JSON and deterministic in ordering.

## Security Non-Goals In This Baseline
Out of scope for this baseline:

- third-party anti-cheat service integration
- invasive client scanning
- client-side prediction integrity proofs
- matchmaking trust federation
