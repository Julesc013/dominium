Status: DERIVED
Last Reviewed: unknown
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: DOC-CONVERGENCE
Replacement Target: canon-aligned documentation set for convergence and release preparation

# GEO-9 Overlay Merge Baseline

Status: baseline complete
Scope: deterministic procedural base plus ordered overlay layers for official packs, mods, and save patches
Readiness: GEO-10 stress envelope and MVP worldgen planning

## Layer Model

Normative precedence:

1. `base.worldgen`
2. `official.reality.*`
3. `mod.*`
4. `save.patch`

Merge behavior:

- effective object views are derived by `src/geo/overlay/overlay_merge_engine.py`
- merge is property-level, not whole-object replace
- canonical patch order is stable by layer precedence, then stable layer sort, then `(property_path, target_object_id, patch hash)`
- overlays may add new objects through stable `object_id` targets but may not silently delete canonical objects
- `remove` operations require explicit reason metadata

Identity and lineage protections:

- `object_id`
- `identity_hash`
- `generator_version_id`
- GEO profile ids (`topology_profile_id`, `metric_profile_id`, `partition_profile_id`, `projection_profile_id`)

These fields are immutable in overlays unless a CompatX migration path is introduced.

## Conflict Resolution

Deterministic resolution rules:

- higher-precedence layer wins
- ties within a precedence tier resolve by stable pack/layer ordering
- official layers must match the active pack lock and signed trust policy
- unsigned mods are policy-gated and explicitly labeled in trust categories
- save patches remain canonical per save and survive official overlay updates because they target stable object IDs

Explainability surfaces:

- `tools/geo/tool_explain_property_origin.py`
- `explain.property_origin`
- `explain.overlay_conflict`

The explain report returns the current winning layer plus the full prior value chain for a property.

## Runtime Surfaces

Authoritative and derived surfaces added in GEO-9:

- overlay merge runtime: `src/geo/overlay/overlay_merge_engine.py`
- save patch process: `process.overlay_save_patch` in `tools/xstack/sessionx/process_runtime.py`
- default overlay manifest seeding: `tools/xstack/sessionx/creator.py`
- replay verification: `tools/geo/tool_replay_overlay_merge.py`
- proof bundle propagation: control/server/shard proof surfaces now carry `overlay_manifest_hash`, `property_patch_hash_chain`, and `overlay_merge_result_hash_chain`

Proof lineage carried for replay and audit:

- `overlay_manifest_hash`
- `property_patch_hash_chain`
- `overlay_merge_result_hash_chain`

## Validation

Validation level: `STRICT`

Results:

- RepoX STRICT: pass
- AuditX STRICT: pass, `promoted_blockers=0`
- GEO-9 TestX subset: pass for the 6 required tests
- overlay replay tool: pass
  - run hash `481d1025e319acafe4b7a4f274c8622606f8ac920df4fd2bd75667d822d08cd5`
- many-overlays stress harness: pass
  - run hash `941ce544057f850221a897de4850605e06b99691747fbe37e2de3705e953085f`
- strict build: pass
  - canonical content hash `9cdabc6762b207303ef749adddf995b3fe64fe1d0605241cf417330f1966e2b5`
- topology map regenerated: pass
  - fingerprint `f8e31b2a7203f13ba84817512c4ae7151faded7f053f6d8cf6a639499962b071`

Not run:

- full repo-wide TestX beyond the GEO-9 subset
- `cmake --preset verify`
- `cmake --build --preset verify`

## GEO-10 Readiness

GEO-9 leaves the repository ready for GEO-10 by freezing:

- stable layer ordering across procedural, official, mod, and save sources
- proofable overlay provenance for effective properties
- deterministic merge and replay surfaces that can scale to large overlay counts
- strict refusal of silent identity or generator-lineage drift
