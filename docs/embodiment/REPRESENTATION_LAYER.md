Status: DERIVED
Version: 1.0.0
Last Reviewed: 2026-02-16
Compatibility: Bound to Truth/Perceived/Render separation, multiplayer epistemic filtering, SecureX governance, and process-only mutation.
Stability: provisional
Future Series: DOC-ARCHIVE
Replacement Target: legacy reference surface retained without current binding authority

# Representation Layer

## Purpose
Define a render-only representation layer so embodied agents can map from capsule/pill proxies to high-fidelity visuals without changing authoritative simulation behavior.

## Authoritative Boundary

1. Truth body primitives (`capsule`, `aabb`, future `convex_hull`) remain the only authoritative interaction geometry.
2. Representation data (mesh, material, LOD, attachments, animation state) is RenderModel-only.
3. Cosmetics must never alter:
   - collision
   - movement
   - reach
   - speed
   - solver/process behavior

## Mapping Contract

1. `body.shape_type` maps to a `render_proxy_id`.
2. Default fallback path is deterministic:
   - missing/invalid proxy -> `render.proxy.pill_default`
3. LOD choice is presentation-only and must not change Truth/Process outcomes.

## Cosmetic Data Model

1. Cosmetic identity:
   - `cosmetic_id`
   - `mesh_id` / `mesh_ref`
   - `material_id` / `material_ref`
   - optional attachment set
2. Cosmetic assignment is server-authored in multiplayer.
3. Preferred storage model for determinism stability:
   - assignments live in Perceived/Render metadata artifacts
   - TruthModel does not carry cosmetic fields

## Ranked/Server Governance

1. Server profiles may bind a cosmetic policy ID.
2. Ranked profiles can require:
   - signed cosmetic packs only
   - explicit cosmetic allow-list
   - SecureX verification
3. Refusals are explicit and deterministic:
   - `refusal.cosmetic.forbidden`
   - `refusal.cosmetic.unsigned_not_allowed`
   - `refusal.cosmetic.not_in_whitelist`

## Mod Safety

1. Cosmetic packs are data-only pack contributions.
2. No executable cosmetic code is allowed in packs.
3. Cosmetic content must be schema-validated and registry-bound.
4. Missing cosmetic packs degrade deterministically to fallback proxy.

## Renderer Independence

1. Null renderer and text-only renderer remain valid execution targets.
2. CLI/TUI output should present a deterministic proxy label (for example, `pill`).
3. Packaging determinism is preserved: assets and registries participate in lockfile hashing; no hidden runtime defaults.
