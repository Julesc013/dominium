Status: DERIVED
Last Reviewed: 2026-03-14
Stability: provisional
Future Series: DIST
Replacement Target: release-pinned component graph audits after install profiles and update channels are frozen

# Component Graph 0 Retro Audit

## Current Dist Reality

- DIST-0 through DIST-6 define a portable bundle layout and verification gates, but bundle composition is still selected by release/dist tooling rather than by a first-class component graph.
- RELEASE-1 `release_manifest.json` enumerates shipped artifacts and hashes, but it does not yet declare dependency edges, provider relationships, or platform-filtered install plans.
- LIB install, instance, and save manifests are already deterministic and content-addressed, but they reference installed content implicitly through pack locks, profile bundles, and install roots rather than a resolved component set.

## Existing Identity Surfaces

- `install.manifest.json` pins product builds, protocol ranges, contract ranges, and store roots.
- `instance.manifest.json` pins required product builds, pack lock hash, profile bundle hash, and install/store locators.
- `save.manifest.json` enforces pack-lock and contract-bundle compatibility.
- `pack_lock.mvp_default.json` is the current authoritative declaration of which packs a default MVP install must ship.
- CAP-NEG endpoint descriptors already expose build IDs, capability sets, platform claims, and contract ranges.

## Implicit Component Assumptions Still Hardcoded

- dist assembly assumes the default bundle always includes all six product entrypoints.
- dist assembly derives included packs by reading the default pack lock directly, not by resolving a release graph.
- setup and launcher can discover and verify installs, but they do not yet produce or inspect an explicit install plan derived from a component graph.
- release manifest generation hashes shipped artifacts, but does not yet bind the manifest to a component graph hash.

## Integration Constraints

- The component graph must remain additive: current dist trees, install manifests, instance manifests, and pack locks must keep loading without migration.
- Resolver output must be deterministic and offline; provider selection must reuse the existing deterministic provides resolver.
- Graph resolution must not invent a new runtime authority path. It may only plan distribution/install composition and validation surfaces.
- `contract.lib.manifest.v1` is still not declared in the current semantic contract registry, so this task must not claim a frozen LIB manifest semantic contract that does not exist.

## Safest Insertion Points

- New release schemas under `schema/release/` and `schemas/`.
- New registries under `data/registries/` for architecture ids and the baseline component graph.
- Resolver in `src/release/` so setup, launcher, release manifest generation, and dist assembly can share one deterministic engine.
- Report/enforcement helpers under `tools/release/` and RepoX/AuditX/TestX.
