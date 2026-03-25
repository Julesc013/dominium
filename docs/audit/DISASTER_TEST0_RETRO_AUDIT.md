# Disaster Test 0 Retro Audit

## Scope

This audit captures the deterministic failure and recovery surfaces already present in the MVP codebase before the Ω-4 freeze.

Audited entrypoints:

- `src/compat/data_format_loader.py`
- `src/compat/migration_lifecycle.py`
- `src/lib/install/install_validator.py`
- `src/lib/provides/provider_resolution.py`
- `src/packs/compat/pack_verification_pipeline.py`
- `src/release/release_manifest_engine.py`
- `src/release/update_resolver.py`
- `src/security/trust/trust_verifier.py`
- `src/universe/universe_contract_enforcer.py`

## Refusal Codes Currently Defined

Primary refusal surfaces already implemented in the audited failure paths:

- Artifact corruption / malformed payloads
  - `refusal.format.schema_invalid`
  - `refusal.release_manifest.manifest_hash_mismatch`
  - `refusal.release_manifest.signature_invalid`
  - `refusal.pack.schema_invalid`
- Missing components
  - `refusal.install.missing_binary`
  - `refuse.bundle_profile.required_pack_missing`
- Compatibility mismatches
  - `refusal.contract.mismatch`
  - `refusal.update.protocol_incompatible`
  - `refusal.migration.not_allowed`
  - `refusal.migration.no_path`
  - `refusal.migration.contract_incompatible`
- Trust failures
  - `refusal.trust.signature_missing`
  - `refusal.trust.signature_invalid`
  - `refusal.trust.root_not_trusted`
  - `refusal.trust.hash_missing`
  - `refusal.trust.policy_missing`
- Policy conflicts
  - `refusal.pack.conflict_in_strict`
  - `refusal.provides.ambiguous`
- Update edge cases
  - `refusal.update.yanked_component`
  - `refusal.update.release_unavailable`
  - `refusal.update.index_missing`

## Remediation Hint Format

Observed deterministic remediation surfaces:

- `src/compat/data_format_loader.py` emits a nested `refusal` object with:
  - `reason_code`
  - `message`
  - `remediation_hint`
- `src/security/trust/trust_verifier.py` emits top-level:
  - `refusal_code`
  - `remediation_hint`
  - plus structured `warnings`
- `src/compat/migration_lifecycle.py` decision rows contain:
  - `refusal_code`
  - `remediation_hint`
  - `decision_action_id`
- `src/release/release_manifest_engine.py` and `src/packs/compat/pack_verification_pipeline.py` carry deterministic error rows keyed by refusal code and ordered error lists

Conclusion:

- Remediation hints are already deterministic strings, but not every subsystem exposes them at the same nesting depth.
- Ω-4 needs a normalization layer so the suite can compare refusal code and remediation hint uniformly across all scenarios.

## Trust Enforcement Points

Current trust enforcement happens at these deterministic choke points:

- `verify_artifact_trust(...)` in `src/security/trust/trust_verifier.py`
- `verify_release_manifest(...)` in `src/release/release_manifest_engine.py`, which delegates manifest trust verification
- `verify_pack_set(...)` in `src/packs/compat/pack_verification_pipeline.py`, which normalizes trust and overlay-conflict refusals

Observed strict-trust behaviors:

- unsigned artifacts refuse in strict mode
- invalid signatures refuse deterministically
- unknown trust roots refuse deterministically
- no network dependency is required for trust evaluation

## Migration Decision Record Format

`src/compat/migration_lifecycle.py` canonicalizes decision records with these stable fields:

- `decision_record_id`
- `artifact_kind_id`
- `observed_version`
- `target_version`
- `decision_action_id`
- `read_only_applied`
- `migration_chain`
- `refusal_code`
- `remediation_hint`
- `deterministic_fingerprint`
- `extensions`

Decision actions already frozen by MIGRATION-LIFECYCLE-0:

- `decision.load`
- `decision.migrate`
- `decision.read_only`
- `decision.refuse`

## Pack Verification Pipeline Outputs

`verify_pack_set(...)` currently returns deterministic pack verification payloads with:

- `result`
- ordered `errors`
- ordered `warnings`
- `overlay_conflict_policy_id`
- selected and resolved pack metadata
- normalized refusal code mapping for overlay conflict and trust denial cases

Important observation:

- pack verification may return `result = complete` while still surfacing ordered `errors`
- Ω-4 must therefore interpret refusal outcome from the normalized error surface, not only from the top-level result field

## Release Index Policy Behavior

`src/release/update_resolver.py` currently implements deterministic release-policy behavior:

- `policy.latest_compatible` sets `allow_yanked = false`
- yanked candidates are skipped deterministically under latest-compatible selection
- explicit yanked selection can still surface `refusal.update.yanked_component` under refusing yank policies
- rollback selection is deterministic via `select_rollback_transaction(...)` over the local install transaction log

Observed implications for Ω-4:

- the "yanked component selected under latest_compatible" scenario should freeze the non-selection behavior, not a silent fallback
- rollback is a deterministic success path when a prior transaction exists and remains part of the failure-recovery model

## Outcome

The repository already contains the refusal, remediation, trust, migration, and update-policy primitives needed for Ω-4. The missing work is not new engine behavior; it is the canonical case registry, deterministic harness, regression baseline, and enforcement surfaces that freeze those behaviors for `v0.0.0-mock`.
