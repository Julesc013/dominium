Status: DERIVED
Version: 1.0.0
Last Reviewed: 2026-02-16
Compatibility: EB-5 representation decoupling baseline for pill->high-fidelity proxy selection and cosmetic governance.

# Representation Baseline

## Scope
This baseline confirms representation decoupling for EB-5:

1. Truth body primitives remain authoritative (`capsule`, `aabb`, `convex_hull` stub).
2. Cosmetic assignment is representation-side metadata and does not mutate TruthModel.
3. RenderModel adapter maps Perceived entity representation to deterministic render proxies.

## Pill Default Path

1. Default proxy ID: `render.proxy.pill_default`.
2. Default mesh/material:
   - `asset.mesh.pill.default`
   - `asset.material.pill.default`
3. Fallback is deterministic when proxy data or assets are missing.
4. CLI/TUI remains valid via deterministic `text_proxy` labels.

## Cosmetic Policy Matrix

1. `policy.cosmetics.private_relaxed`:
   - unsigned packs allowed
   - no whitelist requirement
2. `policy.cosmetics.casual_default`:
   - unsigned packs allowed (warn-focused policy posture)
   - no whitelist requirement by default
3. `policy.cosmetics.rank_strict`:
   - signed packs required
   - whitelist for cosmetic IDs and pack IDs enforced

## Ranked Restrictions

1. Ranked/certified server profiles bind cosmetic policy through registry extensions (`extensions.cosmetic_policy_id`).
2. Unsigned pack assignment under strict policy refuses deterministically:
   - `refusal.cosmetic.unsigned_not_allowed`
3. Non-whitelisted cosmetic under strict policy refuses deterministically:
   - `refusal.cosmetic.not_in_whitelist`

## Determinism Guarantees

1. `process.cosmetic_assign` uses process-only mutation path but writes to `representation_state` sidecar.
2. Cosmetic assignment does not mutate collision/movement fields.
3. Truth outcomes remain stable across cosmetic variations for identical movement intent streams.
4. Render fallback and registry lookups use stable sorted ordering.

## Validation Coverage

1. `test_render_proxy_fallback`
2. `test_cosmetics_do_not_change_truth_outcomes`
3. `test_ranked_refuse_unsigned_cosmetic_pack`
4. `test_private_accept_cosmetic_pack`
5. `test_cosmetic_assign_entitlement_required`

## Extension Points

1. Add new representation packs under `packs/representation/*` with data-only manifests.
2. Extend `render_proxy_registry` and `cosmetic_registry` through registry contributions.
3. Add animation/LOD tuning as RenderModel-only extensions (no Truth coupling).
4. Extend ranked governance with stricter pack publisher constraints via SecureX policy.

