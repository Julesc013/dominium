Status: DERIVED
Last Reviewed: 2026-03-09
Supersedes: none
Superseded By: none
Version: 1.0.0
Compatibility: Bound to `docs/canon/constitution_v1.md`, `docs/canon/glossary_v1.md`, `docs/specs/SPEC_MVP0_SCOPE_CONSTITUTION.md`, `docs/architecture/INSTALL_MODEL.md`, `docs/architecture/session_lifecycle.md`, `tools/xstack/packagingx/dist_build.py`, and `tools/xstack/sessionx/creator.py`.

# MVP1 Retro Audit

## Purpose
Audit the repository's current runtime bundle, install layout, pack naming, profile surfaces, and path assumptions before freezing the v0.0.0 MVP runtime bundle and install layout.

## Summary
The repository already has deterministic bundle, lockfile, SessionSpec, dist, launcher, and pack-loading machinery, but the active runtime surface does not yet match the MVP-1 target shape.

The main mismatches are:

- Active runtime bundles are legacy `bundle.*` pack selections under `bundles/<bundle_id>/bundle.json`; there is no dedicated MVP runtime bundle artifact carrying profile selections.
- Active runtime packs are loaded from top-level `packs/` with `pack.json`, while historical content also exists under `data/packs/` with `pack_manifest.json`.
- Current dist tooling manages `bin/`, `packs/`, `bundles/`, and `registries/` plus root `manifest.json` and `lockfile.json`; it does not create `profiles/`, `locks/`, `saves/`, or `logs/` under `dist/`.
- Existing `pack_lock_hash` is computed from resolved pack rows only; it does not yet incorporate a profile bundle hash.
- Session creation and launcher paths hardcode several repo-relative defaults (`build/lockfile.json`, `build/registries`, `saves`, `dist`, `packs`) that must be documented and then constrained by MVP-1 governance.

## Current Install Layout Assumptions

### Canonical install contract

- `docs/architecture/INSTALL_MODEL.md` defines `INSTALL_ROOT/install.manifest.json` as the authoritative install manifest.
- The install contract is manifest-driven and explicitly rejects hidden single-install assumptions.
- Multiple install manifests may coexist on one machine.

### Active runtime/dist contract

- `tools/xstack/packagingx/dist_build.py` manages a deterministic source-dist layout rooted at `dist/` (or another output root).
- Managed dist subdirectories today are:
  - `bin/`
  - `packs/`
  - `bundles/`
  - `registries/`
- Managed dist root files today are:
  - `manifest.json`
  - `lockfile.json`
- `tools/launcher/launch.py` expects:
  - `dist/manifest.json`
  - `dist/lockfile.json`
  - `dist/registries/*.json`
  - `saves/<save_id>/session_spec.json`

### Session bootstrap assumptions

- `tools/xstack/session_create.py` and `tools/xstack/sessionx/creator.py` create runtime artifacts under `saves/<save_id>/`.
- Session creation currently defaults to:
  - bundle: `bundle.base.lab`
  - scenario: `scenario.lab.galaxy_nav`
  - law: `law.lab.unrestricted`
  - experience: `profile.lab.developer`
  - parameter bundle: `params.lab.placeholder`
  - budget policy: `policy.budget.default_lab`
  - fidelity policy: `policy.fidelity.default_lab`
  - generator version: `gen.v0_stub`
  - realism profile: `realism.realistic_default_milkyway_stub`
- `SessionSpec` already requires `pack_lock_hash`, but the creator resolves it from `build/lockfile.json`, not from a dedicated MVP pack-lock artifact.

## Existing Pack Directories And Naming

### Active pack system

- Active runtime pack discovery uses top-level `packs/`.
- Pack manifests are named `pack.json`.
- Pack paths must be `packs/<category>/<pack_id>/pack.json`.
- Active pack categories are fixed in `tools/xstack/pack_loader/constants.py`:
  - `core`
  - `domain`
  - `derived`
  - `experience`
  - `law`
  - `physics`
  - `representation`
  - `specs`
  - `source`
  - `system_templates`
  - `tool`

### Historical pack content still present

- Historical/archival content also exists under `data/packs/`.
- Those manifests use `pack_manifest.json` and different pack ids such as:
  - `org.dominium.base.universe.milkyway`
  - `org.dominium.base.system.sol`
  - `org.dominium.base.body.earth_macro`
- Those paths are useful provenance for MVP-1 documentation, but they are not the active pack-loading surface used by `tools/xstack/pack_loader/loader.py`.

### Current bundle composition relevant to MVP

- The active default compile/runtime bundle is `bundles/bundle.base.lab/bundle.json`.
- It resolves many packs beyond the MVP-1 minimal target, including law, experience, physics, astronomy, Earth tiles, tools, and policies.
- The active top-level packs closest to the desired MVP world substrate are:
  - `packs/core/pack.core.runtime`
  - `packs/domain/astronomy.milky_way`
  - `packs/domain/astronomy.sol`
  - `packs/domain/planet.earth`

## Existing Profile Registries

### Unified profile surface

- `data/registries/profile_registry.json` already contains profile-style entries for:
  - `physics.default_realistic`
  - `geo.topology.r3_infinite`
  - `geo.metric.euclidean`
  - `geo.partition.grid_zd`
  - `geo.projection.ortho_2d`
  - `geo.projection.perspective_3d`
  - `epistemic.admin_full`
  - `coupling.default`
  - `compute.default`
- The following nearby identifiers do not currently exist exactly as requested by MVP-1:
  - `law.lab_freecam`
  - `law.softcore_observer`
  - `epistemic.diegetic_default` in `profile_registry.json`

### Specialized registries already present

- Specialized registries also exist for runtime resolution, including:
  - `data/registries/space_topology_profile_registry.json`
  - `data/registries/metric_profile_registry.json`
  - `data/registries/partition_profile_registry.json`
  - `data/registries/projection_profile_registry.json`
  - `data/registries/realism_profile_registry.json`
  - `data/registries/generator_version_registry.json`
  - `data/registries/overlay_policy_registry.json`
  - `data/registries/logic_policy_registry.json`
  - `data/registries/compute_budget_profile_registry.json`
  - `data/registries/view_policy_registry.json`
  - `data/registries/session_defaults.json`

### Important identifier mismatch

- `epistemic.diegetic_default` already appears as an epistemic policy id in `data/registries/view_policy_registry.json`.
- `profile_registry.json` instead exposes `epistemic.default_diegetic`.
- MVP-1 must document this mismatch explicitly and avoid silently pretending the names are already unified.

## Hardcoded Paths And Platform Assumptions

### Hardcoded repo-relative runtime paths

- `tools/xstack/sessionx/creator.py`
  - reads and writes `build/lockfile.json`
  - reads `build/registries/*.json`
  - writes `saves/<save_id>/...`
  - reads `data/registries/profile_registry.json`
- `tools/xstack/registry_compile/compiler.py`
  - defaults to `build/registries`
  - defaults to `build/lockfile.json`
  - defaults to top-level `packs/`
- `tools/xstack/packagingx/dist_build.py`
  - defaults to output root `dist`
  - assumes root `lockfile.json` and `manifest.json`
  - assumes `dist/registries` mirrors compiled runtime registries
- `tools/launcher/launch.py`
  - defaults to `dist`
  - defaults to `saves`
  - enforces `dist/lockfile.json` and `dist/registries`
- `client/app/main_client.c`
  - hardcodes `data/scenarios/default.scenario`
  - hardcodes `data/variants/default.variant`

### Install-layout assumptions that diverge from MVP-1

- Dist tooling currently creates `bundles/` and `registries/` but not `profiles/` or `locks/`.
- Dist pack layout today preserves source pack categories (`core`, `domain`, `law`, etc.) rather than the MVP-1 `base/` and `official/` grouping.
- Runtime bundle selection is performed through `bundle_id`; there is no separate `profile_bundle` command surface today.

### Platform assumptions

- Dist tooling emits both POSIX-style stubs and Windows `.cmd` wrappers.
- The repository is Windows-friendly and several examples are Windows-oriented, but the runtime/tooling contracts themselves are still path-normalized and intended to be cross-platform.
- Current path handling generally normalizes separators, but some surfaces still assume repo-root execution or build-root presence rather than explicit install-local discovery.

## Audit Conclusions

- MVP-1 should not replace the existing bundle/lock/dist/session machinery outright.
- MVP-1 should introduce a new authoritative runtime-bundle layer that sits above the existing pack bundle and lockfile surfaces.
- MVP-1 must document and constrain the coexistence of:
  - active top-level `packs/`
  - historical `data/packs/`
  - legacy dist bundle/registry layout
  - new MVP install layout requirements
- MVP-1 enforcement must explicitly guard against:
  - hardcoded `dist/packs/...` usage
  - missing MVP pack lock references
  - missing MVP profile bundle references
  - silent fallback to implicit seeds outside the documented dev default

## Recommended MVP-1 Follow-Through

- Add a dedicated MVP runtime bundle artifact with explicit profile ids and authority defaults.
- Add a dedicated MVP pack-lock artifact whose hash includes ordered pack hashes and the runtime-bundle hash.
- Add a canonical SessionSpec template artifact for the MVP launch path.
- Extend dist with the required MVP layout while preserving legacy dist surfaces still needed by current runtime tooling.
- Add RepoX and AuditX checks so the repo cannot drift back to ad hoc bundle or hardcoded pack-path usage.
