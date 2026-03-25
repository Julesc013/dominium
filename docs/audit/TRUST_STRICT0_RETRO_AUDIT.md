Status: DERIVED
Last Reviewed: 2026-03-25
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: GOVERNANCE/COMMERCIAL
Replacement Target: release-pinned strict trust constitution with signed capability governance

# Trust Strict Retro Audit

## TRUST-MODEL-0 Surfaces

- Core verifier: `src/security/trust/trust_verifier.py`
- Existing trust reporting helper: `tools/security/trust_model_common.py`
- Existing CLI/report runner: `tools/security/tool_run_trust_model.py`
- Existing doctrine: `docs/security/TRUST_AND_SIGNING_MODEL.md`

## Mod Policy Integration

- `src/security/trust/trust_verifier.py::effective_trust_policy_id`
  - `mod_policy.strict` -> `trust.strict_ranked`
  - `mod_policy.lab` -> `trust.default_mock`
  - `mod_policy.anarchy` -> `trust.anarchy`
- `src/modding/mod_policy_engine.py` declares strict-only signed trust levels through policy data, not mode flags.

## Update Resolver Trust Checks

- `src/release/update_resolver.py` verifies `release_index` trust before plan resolution.
- Trust refusal is surfaced through update-plan refusal flow; warnings are preserved in deterministic order.

## Optional vs Required Signatures

- `trust.default_mock`
  - hashes required
  - unsigned `artifact.pack`, `artifact.pack_compat`, `artifact.release_index`, `artifact.release_manifest` warn
- `trust.strict_ranked`
  - signatures required for `artifact.pack`, `artifact.pack_compat`, `artifact.release_index`, `artifact.release_manifest`
  - untrusted roots refuse
- `trust.anarchy`
  - hashes required
  - unsigned governed artifacts accepted without warning escalation

## Existing Refusal Codes

- `refusal.trust.hash_missing`
- `refusal.trust.signature_missing`
- `refusal.trust.signature_invalid`
- `refusal.trust.root_not_trusted`
- `refusal.trust.policy_missing`
- update integration maps trust refusal into `refusal.update.trust_unmet` when update resolution is blocked

## Audit Findings

- Existing trust model already supports deterministic policy selection, warning keys, refusal codes, and offline trust-root verification.
- No existing `artifact.license_capability` surface exists yet.
- Commercialization hook can be added additively by introducing a signed capability artifact and keeping enforcement offline-only.
