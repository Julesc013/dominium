Status: DERIVED
Last Reviewed: 2026-02-14
Supersedes: none
Superseded By: none
Version: 1.0.0
Compatibility: Bound to `schemas/lens.schema.json` v1.0.0, `schemas/law_profile.schema.json` v1.0.0, and compiled `build/registries/lens.registry.json` / `build/registries/law.registry.json`.

# Lens System v1

## Purpose
Define deterministic lens selection and gating rules across SessionSpec boot and Observation Kernel execution.

## Source Artifacts
- Lens contributions:
  - pack contribution type `lens`
  - validated through registry compile into `build/registries/lens.registry.json`
- Law profile contributions:
  - pack contribution type `law_profile`
  - validated through registry compile into `build/registries/law.registry.json`
- Experience profile contributions:
  - optional `default_lens_id` used for default selection.

## Selection Rules (v1)
1. Primary:
   - Experience profile `default_lens_id` for SessionSpec `experience_id`.
2. Fallback:
   - first lexical lens ID in LawProfile `allowed_lenses`.
3. Refusal:
   - no resolvable lens -> `LENS_NOT_FOUND`.

## Gating Rules
- Law gate:
  - selected `lens_id` must be in `allowed_lenses`.
  - refusal code: `LENS_FORBIDDEN`.
- Entitlement gate:
  - all `required_entitlements` from lens payload must be present in AuthorityContext.
  - nondiegetic lenses additionally require `lens.nondiegetic.access`.
  - refusal code: `ENTITLEMENT_MISSING`.

## Determinism Rules
- Lens choice is deterministic from compiled registries and session inputs.
- No runtime mode branch is used for lens behavior.
- Refusal payload fields are deterministic:
  - `reason_code`
  - `message`
  - `remediation_hint`
  - `relevant_ids`

## Example
```json
{
  "experience_id": "profile.lab.developer",
  "law_profile_id": "law.lab.unrestricted",
  "selected_lens_id": "lens.diegetic.sensor",
  "required_entitlements": [
    "session.boot",
    "ui.window.lab.nav"
  ]
}
```

## TODO
- Add LensPack signature trust policy coupling with SecureX checks.
- Add explicit lens-switch command contract for future UI surfaces.
- Add optional lens priority weighting contract for multi-lens experiences.

## Cross-References
- `docs/contracts/lens_contract.md`
- `docs/contracts/law_profile.md`
- `docs/contracts/authority_context.md`
- `docs/contracts/refusal_contract.md`
- `docs/architecture/observation_kernel.md`
- `docs/architecture/truth_perceived_render.md`
