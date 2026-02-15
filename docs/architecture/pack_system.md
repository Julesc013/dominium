Status: DERIVED
Last Reviewed: 2026-02-14
Supersedes: none
Superseded By: none
Version: 1.0.0
Compatibility: Bound to canon v1.0.0, glossary v1.0.0, and `schemas/pack_manifest.schema.json` v1.0.0.

# Pack System v1 Contract

## Purpose
Define strict, deterministic pack composition contracts for data-only modular integration.

## Folder Layout
- Root: `packs/`
- Categories: `packs/core/`, `packs/domain/`, `packs/experience/`, `packs/law/`, `packs/tool/`
- Pack path: `packs/<category>/<pack_id>/`
- Required manifest: `packs/<category>/<pack_id>/pack.json`
- Optional directories inside a pack:
  - `data/`
  - `assets/`
  - `ui/`
  - `scenarios/`

## Bundle Selection (v1)
- Bundle profiles live under `bundles/<bundle_id>/bundle.json`.
- Schema: `schemas/bundle_profile.schema.json` (`version: 1.0.0`).
- Bundle fields:
  - `bundle_id`
  - `description`
  - `pack_ids` (required)
  - `optional_pack_ids` (optional)
- `pack_ids` ordering is not trusted for runtime ordering.
- Dependency resolver computes canonical ordering regardless of bundle declaration order.
- Commands:
  - `tools/xstack/bundle_list`
  - `tools/xstack/bundle_validate bundles/bundle.base.lab/bundle.json`

## Contract Boundaries (Non-Negotiable)
- Packs are data-only.
- Pack identity and compatibility are manifest-declared.
- Runtime behavior resolves from registries and profiles, never runtime mode flags.
- No executable code is allowed under `packs/`.
- Pack activation is explicit through manifest + dependency resolution, never implicit.

## Manifest Contract (`schemas/pack_manifest.schema.json`, `version: 1.0.0`)
- `pack_id`
- `version`
- `compatibility`
- `dependencies[]`
- `contribution_types[]`
- `contributions[]`
- `canonical_hash`
- `signature_status`
- `schema_version` (`const "1.0.0"`)

## Typed Contributions (`v1`)
Supported contribution types:
- `domain`
- `registry_entries`
- `law_profile`
- `experience_profile`
- `lens`
- `ui_windows`
- `assets`
- `scenario_spec`

Each contribution entry requires:
- `type`
- `id`
- `path` (relative to pack directory)

Contribution parsing rules:
- Unsupported types are refused.
- Contribution IDs must be globally unique across all loaded packs.
- Contribution paths must exist and remain inside the owning pack directory.

## Deterministic Dependency Rules
- Dependencies are declared in manifest `dependencies[]`.
- Resolver performs deterministic topological sort.
- Tie-break inside the same dependency level uses lexical `pack_id` ordering.
- Identical input set must always produce identical ordered pack list.

## Refusal Cases
- Duplicate `pack_id`
- Version conflict for the same `pack_id`
- Missing dependency
- Circular dependency
- Unsupported contribution type
- Duplicate contribution ID
- Contribution path missing or escaping pack directory
- Manifest invalid against `schemas/pack_manifest.schema.json`

## No Runtime Branching Rule
- Pack tooling only validates and orders pack data.
- No runtime simulation, engine, renderer, or client branching is introduced by this layer.
- Integration occurs via deterministic compile-time outputs (`registry_compile` + lockfile), not ad hoc runtime merging.
- `tools/xstack/run` invokes bundle validation as step `02.bundle.validate`.
- `tools/xstack/run` invokes pack validation as step `03.pack.validate` before registry compilation.
- Session boot and Observation Kernel consume compiled lens/law/experience registry rows only.
- Lens gating must be profile-driven (`LawProfile` + `AuthorityContext`), never mode flags.

## Example
```json
{
  "schema_version": "1.0.0",
  "pack_id": "pack.domain.navigation",
  "version": "1.0.0",
  "compatibility": {
    "session_spec_min": "1.0.0",
    "session_spec_max": "1.0.0"
  },
  "dependencies": [
    "pack.core.runtime@1.0.0"
  ],
  "contribution_types": [
    "domain",
    "lens",
    "assets"
  ],
  "contributions": [
    {
      "type": "domain",
      "id": "domain.navigation",
      "path": "data/domain.navigation.json"
    },
    {
      "type": "lens",
      "id": "lens.diegetic.sensor",
      "path": "data/lens.sensor.json"
    }
  ],
  "canonical_hash": "placeholder.pack.domain.navigation.v1",
  "signature_status": "signed"
}
```

## Forward Compatibility Strategy
- Manifest versioning remains explicit through schema + CompatX registry.
- Breaking manifest changes require version bump and explicit migration/refusal route.
- Unsupported schema versions refuse deterministically; no silent coercion.
- Bundle composition is locked through `build/lockfile.json` to preserve reproducibility across rebuilds.
- Bundle schema evolution follows CompatX registry policy (`tools/xstack/compatx/version_registry.json`).

## TODO
- Add signed trust policy projection for pack signature verification phases.

## Cross-References
- `docs/canon/constitution_v1.md`
- `docs/canon/glossary_v1.md`
- `docs/architecture/registry_compile.md`
- `docs/architecture/lockfile.md`
- `docs/architecture/deterministic_packaging.md`
- `docs/architecture/setup_and_launcher.md`
- `docs/contracts/session_spec.md`
- `docs/contracts/law_profile.md`
- `schemas/pack_manifest.schema.json`
- `schemas/bundle_profile.schema.json`
- `schemas/bundle_lockfile.schema.json`
- `docs/contracts/versioning_and_migration.md`
- `docs/governance/COMPATX_MODEL.md`
- `docs/architecture/session_lifecycle.md`
- `docs/architecture/lens_system.md`
- `docs/architecture/truth_perceived_render.md`
