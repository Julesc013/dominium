# GEO9 Retro Consistency Audit

Status: DRAFT
Last Reviewed: 2026-03-09
Scope: GEO-9 overlay and patch merge constitution

## Objective

Audit the current repository for pre-existing pack layering, save mutation, and overlay semantics before freezing the GEO-9 merge model.

## Binding Inputs Reviewed

- `docs/canon/constitution_v1.md`
- `docs/canon/glossary_v1.md`
- `docs/geo/WORLDGEN_CONSTITUTION.md`
- `src/geo/worldgen/worldgen_engine.py`
- `tools/xstack/sessionx/creator.py`
- `tools/xstack/sessionx/runner.py`
- `tools/xstack/sessionx/script_runner.py`
- `tools/xstack/registry_compile/lockfile.py`
- representative pack manifests under `data/packs/` and `data/worldgen/real/`

## Findings

### 1. Pack composition and lockfile usage already exist

- Pack composition is already deterministic through `build/lockfile.json` and `tools/xstack/registry_compile/lockfile.py`.
- Lockfiles already carry:
  - `pack_lock_hash`
  - `resolved_packs[*].pack_id`
  - `resolved_packs[*].canonical_hash`
  - `resolved_packs[*].signature_status`
- SecureX tooling already validates lockfile pack signature policy through `tools/security/tool_securex_verify_lockfile.py`.

Implication:
- GEO-9 should not invent a second trust or pack ordering system.
- Overlay manifests should reuse `pack_lock_hash` and resolved-pack signature/trust metadata as input.

### 2. Real-data and authored content already behaves like overlays, but only implicitly

- Real-world worldgen packs such as:
  - `data/packs/org.dominium.worldgen.real.sol/pack_manifest.json`
  - `data/worldgen/real/*/content/refinement_plans.json`
  already describe refinement/override intent with tags like `precedence.overlay`.
- GEO-8 explicitly deferred formal overlay semantics to GEO-9 in `docs/geo/WORLDGEN_CONSTITUTION.md`.

Implication:
- Current overlay intent exists in data, but merge precedence, explainability, and save interaction are not yet canonicalized in code.
- GEO-9 must formalize the layer stack without breaking existing pack content.

### 3. Save representation is snapshot-oriented, not patch-oriented

- Current save boot/resume paths load:
  - `saves/<save_id>/universe_identity.json`
  - `saves/<save_id>/universe_state.json`
- `tools/xstack/sessionx/runner.py` and `tools/xstack/sessionx/script_runner.py` enforce identity stability and pack-lock compatibility, but they do not define a canonical property-patch layer for player edits.
- Existing player/runtime mutations are persisted through the mutable `UniverseState` snapshot and process logs, not through a generalized overlay patch ledger.

Implication:
- GEO-9 must introduce a canonical save patch layer while remaining compatible with snapshot saves.
- Save patches need stable object targeting by `object_id`, not by mutable index or float position.

### 4. Existing overlay semantics are fragmented across domains

- Rendering uses overlay vocabulary for UI and debug surfaces, but that is presentational and not a truth merge contract.
- Terrain and geometry docs mention overlay-like edits, but those are domain-specific process outputs rather than a unified object/property merge substrate.
- There is no repo-wide deterministic merge engine for:
  - base procedural object properties
  - official authored overrides
  - mod overrides
  - save patch overrides

Implication:
- GEO-9 needs a dedicated merge engine instead of reusing renderer overlays or domain-local patch logic.

### 5. Stable identity and lineage constraints already exist and must be preserved

- GEO-1 stable IDs derive from universe identity and `geo_cell_key`.
- GEO-8 locks `generator_version_id` and `realism_profile_id` into `UniverseIdentity`.
- Session resume already refuses lineage drift for generator and realism IDs.

Implication:
- Overlay layers may not silently replace or rewrite `object_id`.
- Topology, metric, and generator lineage remain session-boundary or migration-boundary changes only.

## Drift / Risk Points

### Drift Point A: overlay intent in pack data without canonical merge semantics

- Current refinement plans can imply precedence, but the runtime lacks a canonical property-level resolver.

Risk:
- different consumers could merge the same pack stack differently.

### Drift Point B: save edits have no generalized property patch form

- Save state persistence exists, but there is no canonical `property_patch` record contract.

Risk:
- future official packs could collide with player edits without an auditable precedence model.

### Drift Point C: explainability gap

- The repository can prove lockfile composition and worldgen output hashes, but cannot yet answer property-origin questions like:
  - which layer set a given value
  - which pack hash overrode the base

Risk:
- troubleshooting, migration, and player-facing provenance would be opaque.

## Migration Needs

- Introduce a canonical GEO overlay manifest keyed by pack-lock lineage.
- Represent save edits as stable `property_patch` rows targeting `object_id`.
- Derive effective object views through a deterministic property-level merge engine.
- Preserve snapshot saves while allowing a save patch layer to coexist with `UniverseState`.
- Expose property-origin provenance tooling so conflicts are explainable and replayable.
- Carry overlay manifest and property patch hashes into proof/replay surfaces.

## Non-Goals Confirmed For GEO-9

- no online service dependency
- no silent migration of save identities
- no TruthModel/UI boundary collapse
- no replacement of GEO-8 worldgen base identity
