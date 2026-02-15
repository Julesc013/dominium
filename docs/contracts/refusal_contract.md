Status: DERIVED
Last Reviewed: 2026-02-14
Supersedes: none
Superseded By: none
Version: 1.0.0
Compatibility: Bound to `docs/architecture/REFUSAL_SEMANTICS.md` (REFUSE0), `tools/xstack/sessionx/`, and canonical schemas v1.0.0.

# Refusal Contract

## Purpose
Define deterministic, auditable refusal payloads for tool surfaces (including session create/boot).

## Source of Truth
- `docs/architecture/REFUSAL_SEMANTICS.md`
- `docs/architecture/REFUSAL_AND_EXPLANATION_MODEL.md`
- `tools/xstack/sessionx/common.py`
- Canon binding: `docs/canon/constitution_v1.md`, `docs/canon/glossary_v1.md`

## Required Refusal Shape
All refusals produced by session/bundle tooling must include:
- `reason_code` (stable token)
- `message` (deterministic single-sentence summary)
- `remediation_hint` (deterministic corrective action)
- `relevant_ids` (object map with stable keys such as `bundle_id`, `schema_id`, `save_id`)

Tool payload wrapper:
- `result: "refused"`
- `refusal: { reason_code, message, remediation_hint, relevant_ids }`
- `errors[]`: deterministic projection for legacy tool surfaces.

## Canonical Session/Bundle Refusal Codes (v1)
- `REFUSE_BUNDLE_INVALID`
- `REFUSE_BUNDLE_COMPILE_FAILED`
- `REFUSE_SESSION_SPEC_INVALID`
- `REFUSE_LOCKFILE_MISSING`
- `REFUSE_LOCKFILE_SCHEMA_INVALID`
- `REFUSE_LOCKFILE_HASH_INVALID`
- `REFUSE_LOCKFILE_BUNDLE_MISMATCH`
- `REFUSE_REGISTRY_MISSING`
- `REFUSE_REGISTRY_HASH_MISMATCH`
- `REFUSE_UNIVERSE_IDENTITY_INVALID`
- `REFUSE_UNIVERSE_IDENTITY_MUTATION`
- `REFUSE_UNIVERSE_STATE_INVALID`
- `REFUSE_AUTHORITY_CONTEXT_INVALID`
- `REFUSE_AUTHORITY_ORIGIN_INVALID`
- `REFUSE_RNG_ROOTS_EMPTY`
- `LAW_PROFILE_NOT_FOUND`
- `LENS_NOT_FOUND`
- `ACTIVATION_POLICY_NOT_FOUND`
- `BUDGET_POLICY_NOT_FOUND`
- `FIDELITY_POLICY_NOT_FOUND`
- `LENS_FORBIDDEN`
- `ENTITLEMENT_MISSING`
- `PROCESS_FORBIDDEN`
- `PRIVILEGE_INSUFFICIENT`
- `PROCESS_INPUT_INVALID`
- `REGISTRY_MISSING`
- `TARGET_NOT_FOUND`
- `TARGET_AMBIGUOUS` (reserved for deterministic name-query paths)
- `BUDGET_EXCEEDED`
- `CONSERVATION_VIOLATION`
- `REFUSE_SCRIPT_INVALID`
- `REFUSE_WORKER_COUNT_INVALID`
- `REFUSE_LOGICAL_SHARD_COUNT_INVALID`
- `SHARD_TARGET_INVALID`
- `SRZ_SHARD_INVALID`
- `LOCKFILE_MISMATCH`
- `PACK_INCOMPATIBLE`
- `REGISTRY_MISMATCH`
- `refusal.domain_missing`
- `refusal.contract_missing`
- `refusal.solver_unbound`
- `refusal.duplicate_id`
- `refusal.contract_violation`
- `REFUSE_DIST_MANIFEST_INVALID`
- `REFUSE_DIST_CONTENT_HASH_MISMATCH`
- `refusal.server_stage_mismatch`
- `refusal.server_authority_violation`
- `refusal.net.handshake_pack_lock_mismatch`
- `refusal.net.handshake_registry_hash_mismatch`
- `refusal.net.handshake_schema_version_mismatch`
- `refusal.net.handshake_policy_not_allowed`
- `refusal.net.handshake_securex_denied`
- `refusal.net.envelope_invalid`
- `refusal.net.sequence_violation`
- `refusal.net.replay_detected`
- `refusal.net.authority_violation`
- `refusal.net.shard_target_invalid`
- `refusal.net.cross_shard_unsupported`
- `refusal.net.perception_policy_missing`
- `refusal.net.resync_required`
- `refusal.net.resync_snapshot_missing`
- `refusal.net.join_snapshot_invalid`
- `refusal.net.join_policy_mismatch`
- `refusal.ac.policy_violation`
- `refusal.ac.rank_policy_required`
- `refusal.ac.attestation_missing`

## Multiplayer Refusal Remediation Hints (MP-1)
- `refusal.net.handshake_pack_lock_mismatch`: reconnect using identical bundle + lockfile; regenerate client dist if needed.
- `refusal.net.handshake_registry_hash_mismatch`: rebuild registries + lockfile from same bundle input set and reconnect.
- `refusal.net.handshake_schema_version_mismatch`: migrate payload/schema version via CompatX or downgrade to supported schema set.
- `refusal.net.handshake_policy_not_allowed`: choose a replication policy permitted by server law/profile registry.
- `refusal.net.handshake_securex_denied`: satisfy SecureX signing/attestation policy or connect to a less restrictive server.
- `refusal.net.envelope_invalid`: validate `intent_envelope` schema fields and deterministic sequence metadata.
- `refusal.net.sequence_violation`: resend envelopes with monotonic deterministic sequence ordering.
- `refusal.net.replay_detected`: discard replayed envelope IDs and emit fresh deterministic sequence numbers.
- `refusal.net.authority_violation`: submit intents only with allowed authority/law entitlements.
- `refusal.net.shard_target_invalid`: route envelope to declared shard ownership scope.
- `refusal.net.cross_shard_unsupported`: restrict process intent targets to a single owning shard until cross-shard transition support is declared.
- `refusal.net.perception_policy_missing`: configure a valid `perception_interest_policy_id` on the active server policy and rebuild registries.
- `refusal.net.resync_required`: execute policy-specific resync strategy then retry intent stream.
- `refusal.net.resync_snapshot_missing`: generate/request an authoritative snapshot before resync/join retry.
- `refusal.net.join_snapshot_invalid`: run baseline sync first or request a valid snapshot_id from server.
- `refusal.net.join_policy_mismatch`: join using the negotiated replication policy for the active session.
- `refusal.ac.policy_violation`: inspect anti-cheat module events and satisfy declared anti-cheat policy constraints.
- `refusal.ac.rank_policy_required`: select anti-cheat policy with `required_for_ranked=true` before ranked session entry.
- `refusal.ac.attestation_missing`: provide client attestation artifact when policy explicitly enables attestation checks.

## Invariants
- Refusals do not mutate authoritative state.
- Refusals are never silent.
- `reason_code` tokens are stable once released.
- Identical conditions must emit identical refusal payloads (except run-meta timestamps).
- `relevant_ids` must not expose absolute local paths.
- Lens and observation refusals use stable reason codes without mode-flag language.

## Example
```json
{
  "result": "refused",
  "refusal": {
    "reason_code": "REFUSE_LOCKFILE_MISSING",
    "message": "build/lockfile.json is missing",
    "remediation_hint": "Run tools/xstack/lockfile_build --bundle bundle.base.lab --out build/lockfile.json.",
    "relevant_ids": {
      "bundle_id": "bundle.base.lab"
    }
  },
  "errors": [
    {
      "code": "REFUSE_LOCKFILE_MISSING",
      "message": "build/lockfile.json is missing",
      "path": "$.lockfile"
    }
  ]
}
```

## TODO
- Publish machine-readable refusal JSON schema wrapper for payload validation.
- Add deterministic localization contract for `message` projection.
- Add refusal telemetry retention policy and redaction rules.

## Cross-References
- `docs/contracts/authority_context.md`
- `docs/contracts/law_profile.md`
- `docs/architecture/srz_contract.md`
- `docs/architecture/session_lifecycle.md`
