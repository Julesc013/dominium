Status: DERIVED
Version: 1.0.0
Last Reviewed: 2026-02-15
Compatibility: Bound to LawProfile, AuthorityContext, SecureX policy registry, anti-cheat policy registry, and refusal contract.

# Ranked Server Governance

## Purpose
Define ranked/esports governance as policy composition, not runtime mode flags.

## Ranked Definition
Ranked is declared by data:

1. `server_profile_id`
2. `securex_policy_id`
3. `anti_cheat_policy_id`
4. `law_profile_id`
5. lockfile + registry hash compatibility

No `ranked_mode` or similar mode flags are allowed.

## Governance Composition

1. Server boot selects `server_profile_id` from compiled server profile registry.
2. Server governance definitions are pack-contributed data (`pack.server.governance`) and compiled into canonical registries.
3. Server profile declares:
   - allowed replication policies
   - required anti-cheat policy
   - required SecureX policy
   - default epistemic policy
   - allowed/required law profiles
   - entitlement allow/deny lists
4. Handshake validates client request against the selected server profile.
5. Refusal is deterministic on the first failing gate.

## Deterministic Acceptance Order

1. `pack_lock_hash`
2. registry hashes
3. schema version compatibility
4. replication policy allowability
5. anti-cheat policy requirement
6. SecureX policy + signature posture
7. law profile negotiation under server profile constraints

## Policy Matrix

1. `server.profile.rank_strict`
   - Requires strict anti-cheat policy.
   - Requires strict SecureX policy.
   - Forbids observer-truth law profiles.
2. `server.profile.casual_public`
   - Uses casual anti-cheat/SecureX policy.
   - Allows broader replication options.
3. `server.profile.private_relaxed`
   - Allows relaxed SecureX and anti-cheat posture by explicit policy.
   - May allow observer tooling when law profile permits.

## Refusal Behavior
Server must emit explicit deterministic refusals for governance failures:

1. `refusal.net.handshake_policy_not_allowed`
2. `refusal.net.handshake_securex_denied`
3. `refusal.ac.rank_policy_required`
4. `refusal.net.handshake_pack_lock_mismatch`
5. `refusal.net.handshake_registry_hash_mismatch`
6. `refusal.net.handshake_schema_version_mismatch`

## Cross-References

- `docs/security/SECUREX_TRUST_MODEL.md`
- `docs/net/HANDSHAKE_AND_COMPATIBILITY.md`
- `docs/net/ANTI_CHEAT_POLICY_FRAMEWORK.md`
- `docs/contracts/refusal_contract.md`
- `data/registries/server_profile_registry.json`
- `data/registries/securex_policy_registry.json`
