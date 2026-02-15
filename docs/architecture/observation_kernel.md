Status: DERIVED
Last Reviewed: 2026-02-14
Supersedes: none
Superseded By: none
Version: 1.0.0
Compatibility: Bound to canon v1.0.0 and implemented in `tools/xstack/sessionx/observation.py`.

# Observation Kernel v1 Contract

## Purpose
Define the deterministic function that projects truth into observer-visible perception under law, authority, and lens constraints.

## Function Contract
`observe(truth_model, lens, law_profile, authority_context, viewpoint_id) -> perceived_model | refusal`

## Required Inputs
- `truth_model`
  - `universe_identity_ref`
  - `universe_state_ref`
  - `registry_refs`
- `viewpoint_id`
- `lens_id`
- `law_profile_id`
- `authority_context`:
  - `authority_origin`
  - `experience_id`
  - `law_profile_id`
  - `entitlements`
  - `epistemic_scope`
  - `privilege_level`

## Output Fields
- `perceived_model`
  - `viewpoint_id`
  - `lens_id`
  - `epistemic_scope`
  - `observed_entities[]`
  - `observed_fields[]`
  - `camera_viewpoint`
  - `time_state`
  - `metadata` (`simulation_tick`, `coordinate_frame`, `lens_type`)
- `perceived_model_hash` (canonical SHA-256)

## Invariants
- Read-only relative to authoritative state.
- Deterministic output for identical inputs.
- No hidden truth leaks.
- Unknown data remains unknown unless lawful observation/communication/memory resolves it.
- Refusals must follow canonical refusal semantics.
- Observation is gated by both LawProfile `allowed_lenses` and AuthorityContext `entitlements`.
- Nondiegetic lens usage requires explicit entitlement (`lens.nondiegetic.access`).
- Canonical refusal reason codes include `LENS_FORBIDDEN` and `ENTITLEMENT_MISSING`.
- Camera/time viewpoint fields are included only within lawful epistemic limits.

## Example
```json
{
  "viewpoint_id": "viewpoint.client.save.lab.bootstrap",
  "lens_id": "lens.diegetic.sensor",
  "authority_context": {
    "authority_origin": "client",
    "experience_id": "profile.lab.developer",
    "law_profile_id": "law.lab.unrestricted",
    "entitlements": [
      "session.boot",
      "ui.window.lab.nav"
    ],
    "epistemic_scope": {
      "scope_id": "epistemic.lab.placeholder",
      "visibility_level": "placeholder"
    },
    "privilege_level": "observer"
  }
}
```

## TODO
- Add persistence contract for optional PerceivedModel snapshots per run ID.
- Add coordinate-frame transform matrix contract once coordinate system docs are finalized.
- Add deterministic multi-viewpoint batching strategy.

## Cross-References
- `docs/canon/constitution_v1.md`
- `docs/architecture/truth_perceived_render.md`
- `docs/contracts/authority_context.md`
- `docs/contracts/lens_contract.md`
- `docs/contracts/refusal_contract.md`
