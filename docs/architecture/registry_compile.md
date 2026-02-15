Status: DERIVED
Last Reviewed: 2026-02-14
Supersedes: none
Superseded By: none
Version: 1.0.0
Compatibility: Bound to canon/glossary v1.0.0, `tools/xstack/registry_compile/`, and `tools/xstack/cache_store/`.

# Registry Compile v1 Contract

## Purpose
Define deterministic compilation of pack contributions into derived registry artifacts and lockfile outputs.

## Inputs
- Pack manifests discovered from `packs/<category>/<pack_id>/pack.json`
- Deterministically resolved pack order from `tools/xstack/pack_loader/dependency_resolver.py`
- Typed contributions from `tools/xstack/pack_contrib/parser.py`
- Bundle selection from `bundles/<bundle_id>/bundle.json`
- Tool version (`registry_compile` compiler version)

## Outputs
Default output root: `build/registries/`
- `domain.registry.json`
- `law.registry.json`
- `experience.registry.json`
- `lens.registry.json`
- `activation_policy.registry.json`
- `budget_policy.registry.json`
- `fidelity_policy.registry.json`
- `astronomy.catalog.index.json`
- `site.registry.index.json`
- `ui.registry.json`

Default lockfile path:
- `build/lockfile.json`

Cache output root:
- `.xstack_cache/registry_compile_cache/<cache_key>/`

## XStack Invocation
XStack FAST/STRICT/FULL profiles invoke registry compile through:
- `tools/xstack/run`
- step `04.registry.compile`

Direct command equivalents:
- `tools/xstack/bundle_list`
- `tools/xstack/bundle_validate bundles/bundle.base.lab/bundle.json`
- `tools/xstack/registry_compile.cmd`
- `tools/xstack/lockfile_build.cmd --bundle bundle.base.lab --out build/lockfile.json`
- `tools/setup/build --bundle bundle.base.lab --out dist` (consumes compiled lockfile/registries for packaging)

## Boot-Time Expectations
- Session boot (`tools/xstack/session_boot`) requires compiled registries to exist and match lockfile hashes.
- Dist launch (`tools/launcher/launch`) requires packaged registries to match packaged lockfile hashes.
- Boot may refuse if registry files are missing or if lockfile hashes do not match canonical registry payload hashes.
- Optional boot compile is explicit (`--compile-if-missing on`); no silent regeneration.

## Pipeline
1. Load packs via `tools/xstack/pack_loader/loader.py`.
2. Resolve dependencies deterministically via topological ordering with `pack_id` tie-break.
3. Parse typed contributions via `tools/xstack/pack_contrib/parser.py`.
4. Validate contribution payloads for registry-required fields.
5. Compile derived registries:
   - `domain.registry.json`
   - `law.registry.json`
   - `experience.registry.json`
   - `lens.registry.json`
   - `activation_policy.registry.json`
   - `budget_policy.registry.json`
   - `fidelity_policy.registry.json`
   - `astronomy.catalog.index.json`
   - `site.registry.index.json`
   - `ui.registry.json`
6. Emit lockfile (`build/lockfile.json` by default).
7. Store/reuse outputs through content-addressed cache.

## Derived Artifact Fields (Minimum)
Each registry includes:
- `format_version: "1.0.0"`
- `generated_from[]` (`pack_id`, `version`, `canonical_hash`, `signature_status`)
- typed content rows
- `registry_hash`

Observation-gating fields emitted in v1:
- `law.registry.json` rows include:
  - `allowed_lenses[]`
  - `epistemic_limits`
- `lens.registry.json` rows include:
  - `transform_description`
  - `required_entitlements[]`
  - `epistemic_constraints`
- `experience.registry.json` rows may include:
  - `default_lens_id`
  - `default_law_profile_id`
- `astronomy.catalog.index.json` rows include:
  - `entries[]` validated from `schemas/astronomy_catalog_entry.schema.json`
  - `reference_frames[]` validated from `schemas/reference_frame.schema.json`
  - `search_index` (`normalized_search_key -> sorted object_id[]`)
- `site.registry.index.json` rows include:
  - `sites[]` validated from `schemas/site_entry.schema.json`
  - `search_index` (`normalized_search_key -> sorted site_id[]`)
- `activation_policy.registry.json` rows include:
  - `policy_id`
  - `interest_radius_rules`
  - `activation_thresholds`
  - `hysteresis`
- `budget_policy.registry.json` rows include:
  - `policy_id`
  - `activation_policy_id`
  - `max_compute_units_per_tick`
  - `max_entities_micro`
  - `max_regions_micro`
  - `fallback_behavior`
- `fidelity_policy.registry.json` rows include:
  - `policy_id`
  - `tiers`
  - `switching_rules`
  - `minimum_tier_by_kind`

## Deterministic Ordering Rules
- Pack set ordering: deterministic dependency sort, then lexical `pack_id`.
- Contribution ordering: `(contrib_type, id, pack_id)`.
- Registry rows: stable lexical ordering by ID then `pack_id`.
- Canonical hash input uses sorted object keys and UTF-8 canonical JSON serialization.

## Invariants
- No runtime simulation behavior is implemented in compile tooling.
- No implicit defaults for required contribution payload fields.
- Refusals are deterministic and stable-sorted.
- No nondeterministic timestamps in canonical artifacts.

## Cache Store Key Definition
Cache key is Merkle hash over:
- sorted canonical pack manifests
- sorted canonical contribution descriptors (`type`, `id`, `path`, `pack_id`)
- canonical bundle selection
- registry compile tool version

Cache location:
- `.xstack_cache/registry_compile_cache/<cache_key>/`

Cache behavior:
- cache hit: copy stored outputs and lockfile back to target paths without recompute
- cache miss: compile, write outputs, and store new entry with run-meta manifest

## Refusal Cases
- Missing contribution path
- Unsupported contribution type
- Duplicate contribution IDs
- Dependency resolution failure (missing, cycle, version mismatch)
- Manifest/schema validation failure
- Required registry payload fields missing
- Invalid astronomy/site/frame contribution payload shape
- Missing `entry_type` arrays for `registry_entries` payloads

## Domain Data Validation
Registry compile validates domain data contributions in deterministic order:
1. `entry_type: astronomy_catalog_collection` -> each row validated against `schemas/astronomy_catalog_entry.schema.json`
2. `entry_type: reference_frame_collection` -> each row validated against `schemas/reference_frame.schema.json`
3. `entry_type: site_collection` -> each row validated against `schemas/site_entry.schema.json`
4. `entry_type: activation_policy` -> payload validated against `schemas/activation_policy.schema.json`
5. `entry_type: budget_policy` -> payload validated against `schemas/budget_policy.schema.json`
6. `entry_type: fidelity_policy` -> payload validated against `schemas/fidelity_policy.schema.json`

Registry compile builds deterministic search maps by normalization:
- lowercase
- trim leading/trailing whitespace
- collapse interior whitespace to a single ASCII space
- Unicode normalized to NFKD, then non-ASCII removed for index keys

## Lockfile Computation
- Schema: `schemas/bundle_lockfile.schema.json` v1.0.0
- Lock payload includes resolved pack projection + registry hashes + compatibility version.
- `pack_lock_hash` is computed from canonical JSON hash of sorted resolved pack entries:
  - sort key: `pack_id`, `version`, `canonical_hash`, `signature_status`
- `tools/xstack/registry_compile/lockfile.py` performs validation and mismatch refusal.
- XStack step `05.lockfile.validate` enforces schema + `pack_lock_hash` validation on `build/lockfile.json`.

## TODO
- Add explicit registry promotion policy (canonical vs derived) once publish workflow exists.
- Add selective bundle profile variants beyond `bundle.base.lab`.
- Add strict schema validation for contribution payload internals per contribution subtype.

## Cross-References
- `docs/canon/constitution_v1.md`
- `docs/architecture/pack_system.md`
- `docs/architecture/astronomy_catalogs.md`
- `docs/architecture/site_registry.md`
- `docs/architecture/session_lifecycle.md`
- `docs/architecture/lockfile.md`
- `docs/architecture/deterministic_packaging.md`
- `docs/contracts/versioning_and_migration.md`
- `schemas/bundle_lockfile.schema.json`
- `schemas/domain_registry.schema.json`
- `schemas/law_registry.schema.json`
- `schemas/experience_registry.schema.json`
- `schemas/lens_registry.schema.json`
- `schemas/astronomy_catalog_index.schema.json`
- `schemas/site_registry_index.schema.json`
- `schemas/activation_policy_registry.schema.json`
- `schemas/budget_policy_registry.schema.json`
- `schemas/fidelity_policy_registry.schema.json`
- `schemas/ui_registry.schema.json`
