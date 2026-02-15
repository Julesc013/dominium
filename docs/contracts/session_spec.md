Status: DERIVED
Last Reviewed: 2026-02-14
Supersedes: none
Superseded By: none
Version: 1.0.0
Compatibility: Bound to `schemas/session_spec.schema.json` v1.0.0 and CompatX `tools/xstack/compatx/version_registry.json`.

# SessionSpec Contract

## Purpose
Define the canonical, deterministic session bootstrap payload for profile-driven execution.

## Source of Truth
- Schema: `schemas/session_spec.schema.json` (`version: 1.0.0`)
- Related schema: `schemas/authority_context.schema.json`
- SRZ-related schema: `schemas/intent_envelope.schema.json`
- Canon binding: `docs/canon/constitution_v1.md`, `docs/canon/glossary_v1.md`
- Session lifecycle: `docs/architecture/session_lifecycle.md`

## Required Fields (`v1.0.0`)
- `schema_version` (`const "1.0.0"`)
- `universe_id` (string)
- `save_id` (string)
- `scenario_id` (string)
- `mission_id` (string or null)
- `experience_id` (string)
- `parameter_bundle_id` (string)
- `authority_context` (object)
- `pack_lock_hash` (sha256 hex string)
- `budget_policy_id` (string)
- `fidelity_policy_id` (string)
- `deterministic_rng_roots` (array of `{stream_name, root_seed}`)

## Optional Fields (`v1.0.0`)
- `bundle_id` (string)
  - Used by tooling to bind lockfile/registry preparation.
  - If omitted, tooling may use explicit CLI bundle selection (`bundle.base.lab` default).

## Invariants
- No mode flags; all behavior composition is profile data.
- `mission_id` null is valid and must be explicit.
- `authority_context` must be present and valid before admission.
- `pack_lock_hash` must be deterministic and replay-stable.
- `budget_policy_id` and `fidelity_policy_id` must resolve in compiled policy registries.
- No implicit policy defaults are admitted at process runtime.
- Unknown top-level fields are refused by strict validation.
- Session creator writes canonical JSON under `saves/<save_id>/session_spec.json`.
- Session boot resolves default lens from compiled experience/law/lens registries; SessionSpec remains profile-driven.
- Runtime process submission is envelope-based (`schemas/intent_envelope.schema.json`) and must preserve deterministic sequence numbers.

## SRZ Envelope Linkage
`SessionSpec` does not inline envelopes, but it provides the authority and policy context used to construct them at runtime:
- `authority_context.authority_origin` -> `intent_envelope.authority_origin`
- deterministic script order -> `intent_envelope.deterministic_sequence_number`
- scheduler tick at submission -> `intent_envelope.submission_tick`
- v1 runtime enforces `target_shard_id = "shard.0"`

## Example JSON (`schemas/session_spec.schema.json`)
```json
{
  "schema_version": "1.0.0",
  "universe_id": "universe.f7f79f62a426e393",
  "save_id": "save.lab.bootstrap",
  "bundle_id": "bundle.base.lab",
  "scenario_id": "scenario.lab.galaxy_nav",
  "mission_id": null,
  "experience_id": "profile.lab.developer",
  "parameter_bundle_id": "params.lab.placeholder",
  "authority_context": {
    "authority_origin": "client",
    "experience_id": "profile.lab.developer",
    "law_profile_id": "law.lab.unrestricted",
    "entitlements": [
      "session.boot",
      "entitlement.camera_control",
      "entitlement.teleport",
      "entitlement.time_control",
      "lens.nondiegetic.access",
      "ui.window.lab.nav"
    ],
    "epistemic_scope": {
      "scope_id": "epistemic.lab.placeholder",
      "visibility_level": "placeholder"
    },
    "privilege_level": "operator"
  },
  "pack_lock_hash": "06814824a8c7e49d8f577c7aabc88de066e4efab5044f8cf818df491b8535900",
  "budget_policy_id": "policy.budget.default_lab",
  "fidelity_policy_id": "policy.fidelity.default_lab",
  "deterministic_rng_roots": [
    {
      "stream_name": "rng.session.core",
      "root_seed": "0d34f20bbfe8d44f22573afd356fd39c784b6d0bec295f4b3032fd665a5f0a15"
    },
    {
      "stream_name": "rng.session.ui",
      "root_seed": "67b1103bc5cd75c9f868bd168e9b4eb7aeb0c0dc51b85a89f9c31fd57ec32fbc"
    }
  ]
}
```

## TODO
- Add explicit mission binding constraints once `MissionSpec` schema is introduced.
- Add machine-readable session transition compatibility matrix for profile switches.
- Add future migration example once `2.0.0` contracts exist.

## Cross-References
- `docs/contracts/authority_context.md`
- `docs/contracts/versioning_and_migration.md`
- `docs/architecture/pack_system.md`
- `docs/architecture/session_lifecycle.md`
