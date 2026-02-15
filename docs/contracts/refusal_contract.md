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
- `REFUSE_DIST_MANIFEST_INVALID`
- `REFUSE_DIST_CONTENT_HASH_MISMATCH`

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
