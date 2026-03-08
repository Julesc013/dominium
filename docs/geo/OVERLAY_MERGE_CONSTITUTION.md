# GEO-9 Overlay & Patch Merge Constitution

Status: DRAFT
Last Reviewed: 2026-03-09
Owners: GEO / PROV / CompatX

## Purpose

Define the canonical universe layer stack that composes procedural base generation, official reality packs, mod packs, and save patches without breaking stable identity, determinism, or replayability.

## Binding Invariants

- `docs/canon/constitution_v1.md` A1 Determinism is primary
- `docs/canon/constitution_v1.md` A2 Process-only mutation
- `docs/canon/constitution_v1.md` A6 Provenance is mandatory
- `docs/canon/constitution_v1.md` A7 Observer-Renderer-Truth separation
- `docs/canon/constitution_v1.md` A9 Pack-driven integration
- `docs/canon/constitution_v1.md` E4 Named RNG streams
- `docs/canon/constitution_v1.md` E6 Replay equivalence
- `docs/canon/constitution_v1.md` C3 CompatX obligations

## 1. Normative Layer Order

The effective universe view for a cell or object is composed from these ordered layers:

1. `base.worldgen`
2. `official.reality.*`
3. `mod.*`
4. `save.patch`

Rules:

- lower-numbered layers provide defaults
- higher-numbered layers may override supported properties
- precedence is deterministic and data-declared
- ties inside the same precedence class resolve by stable pack ordering using pack hash sort

## 2. Scope of Overlay Application

GEO-9 merge applies to canonical world/model properties, not UI overlays.

Typical merge targets:

- object scalar properties
- object reference properties such as profile/spec ids
- field initializations scoped to a `geo_cell_key`
- macro geometry cell states
- additive system template placements

GEO-9 does not authorize direct Truth mutation by the renderer or lens stack.

## 3. What May Be Overridden

Allowed without migration:

- scalar values via property-level `set`
- additive list/map entries via `add`
- value replacement via `replace`
- explicit property removal via `remove` when the patch records a reason
- new object introduction using stable `object_id`

Constraints:

- resolution is property-level, not whole-object blind replacement
- patches must target canonical property paths
- per-object provenance must remain reconstructable

## 4. What May Not Be Overridden Without Migration

The following are immutable across overlay merge unless a CompatX migration explicitly says otherwise:

- `object_id`
- `generator_version_id`
- topology / metric / partition / projection lineage for an active universe
- session-lineage identity anchors recorded in `UniverseIdentity`

Consequences:

- overlays may not silently rename or replace canonical identities
- overlays may refine or annotate an object, but not change which object it is
- deleting a canonical object requires explicit migration/refusal semantics, not a hidden patch

## 5. Conflict Resolution

Conflict resolution is deterministic.

For the same target property:

1. sort by `precedence_order`
2. then by normalized layer kind rank:
   - `base`
   - `official`
   - `mod`
   - `save`
3. then by stable `source_ref` ordering
4. then by `(property_path, target_object_id, patch hash)`

The final applied value is the last lawful patch in that deterministic order.

If a patch is unlawful:

- it is refused explicitly
- the refusal is stable and replayable
- lower lawful values remain intact

## 6. Deletion Rules

Silent deletion is forbidden.

Normative rules:

- `remove` must be explicit
- `remove` must include a deterministic reason in patch metadata
- removing a canonical object identity requires migration semantics, not merge semantics
- if deletion is not lawful, merge returns a refusal/explanation rather than dropping the object

## 7. Explainability and Provenance

Every effective property must be explainable.

For any `object_id + property_path`, the system must be able to answer:

- which layer set the current value
- which `source_ref` or pack hash supplied it
- which prior values were overridden
- whether a save patch or official/mod pack won the conflict

Required explain surfaces:

- `explain.overlay_conflict`
- `explain.property_origin`

## 8. Save Patch Layer

Player or save-authored edits are represented as canonical `property_patch` records.

Save patch requirements:

- target stable `object_id`
- remain valid across official/mod overlays where identity is unchanged
- be process-produced and auditable
- survive compaction through canonical patch hash chains

Snapshot saves may continue to exist, but GEO-9 formalizes the canonical patch layer that sits above base and pack layers.

## 9. Pack Trust Hooks

Overlay manifests reuse lockfile lineage rather than inventing a second pack identity system.

Normative inputs:

- `pack_lock_hash`
- resolved pack hashes
- SecureX signature/trust classification

Policy:

- official overlay layers require signed or official trust status and a matching lockfile lineage
- mod layers may be unsigned, but the trust category must be explicit and inspectable
- release-grade validation may refuse manifests whose official layers are not backed by the current lockfile

## 10. Determinism and Caching

Merge must be pure and cacheable from:

- base object inputs
- overlay manifest
- property patch rows
- merge engine version

Cache eviction must not change merge output.

Recommended cache key:

`H(base inputs hash, overlay_manifest hash, property_patch hash chain, merge_engine_version)`

## 11. Proof and Replay

Proof bundles for sessions using GEO-9 should include:

- `overlay_manifest_hash`
- `property_patch_hash_chain`
- optional selected `overlay_merge_result_hash_chain`

Replay must regenerate the same effective object view from identical base inputs, manifest, and patches.

## 12. CompatX and Migration Boundary

Any change that alters:

- identity semantics
- generator lineage
- topology lineage
- canonical property path meaning

requires explicit CompatX migration or explicit refusal.

GEO-9 merge is not a migration bypass.

## 13. Non-Goals

- GEO-9 does not implement real-world data packs themselves
- GEO-9 does not authorize executable code in packs
- GEO-9 does not merge UI/render overlays into truth
- GEO-9 does not replace process/event provenance
