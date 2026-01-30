# Launcher and Setup Contract (SHIP-0)

Status: binding.
Scope: installation, discovery, and launch behavior for all distributions.

This contract is about **file selection and validation**, not gameplay or
simulation behavior.

## Distribution Profiles
Two official distribution profiles differ only by bundled files.

### Minimal Distribution (Code-Only)
Includes:
- All binaries: engine, game, client, server, launcher, setup, tools.
- No packs bundled, or only absolute-minimum ontology packs if unavoidable.

Guarantees:
- Application boots.
- Main menu and world creation work.
- Empty/minimal worlds function.
- Suitable for CI, developers, and legacy hardware.

### Maximal Distribution (Official Bundle)
Includes:
- Same binaries as minimal.
- Bundled official packs from `docs/distribution/PACK_TAXONOMY.md`.
- Tutorials and examples.

Guarantees:
- Playable out of the box.
- No first-run downloads required.

Critical rule:
Launcher and Setup MUST NOT branch behavior based on distribution. They only
detect which files are present.

## Setup Responsibilities
Setup installs binaries and creates a data root. It MUST NOT:
- Install content by default.
- Mutate pack contents.
- Create special cases for minimal vs maximal distributions.

Setup MAY:
- Create empty pack/mod directories.
- Validate basic filesystem permissions.
 - Emit install and instance manifests (`docs/architecture/INSTALL_MODEL.md`,
   `docs/architecture/INSTANCE_MODEL.md`).

## Launcher Responsibilities
Launcher is read-only by default and must:
- Discover packs present on disk.
- Validate manifest compatibility and report issues.
- Operate relative to explicit install/instance manifests.
- Generate capability lockfiles on save/world creation.
- Respect existing lockfiles without silent changes.
- Offer profile-based recommendations (data-driven; see `schema/profile.schema`).
- Allow fully custom selection.

Launcher MUST NOT:
- Assume any pack is present.
- Require network access.
- Alter simulation semantics.

## Pack sources
Pack resolution uses ordered sources defined by `docs/distribution/PACK_SOURCES.md`.

## Lockfiles and Determinism
Lockfiles are authoritative for capability resolution and must be deterministic.
Launcher behavior:
- On world creation, generate a capability lockfile.
- On load, refuse if required capabilities cannot be satisfied.
- Warn when recommended packs are missing.
- Never silently replace or reorder capability providers.

## Pack Discovery Rules
- Pack manifests are discovered without reading pack contents.
- Discovery order is deterministic.
- Absence of packs is valid and must not crash or block UI entry.

## See also
- `docs/distribution/SETUP_GUARANTEES.md`
- `docs/distribution/SETUP_GUIDE.md`
- `docs/distribution/OFFLINE_INSTALL.md`
- `docs/distribution/UNINSTALL_AND_REPAIR.md`
- `docs/architecture/SETUP_TRANSACTION_MODEL.md`
- `docs/distribution/LAUNCHER_SCOPE.md`
- `docs/distribution/LAUNCHER_GUIDE.md`
