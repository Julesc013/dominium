# Contracts Manifest

Status: PROVISIONAL
Phase: CONVERGE-06
Date: 2026-05-12

CONVERGE-06 converged safe schema and schema-projection roots under `contracts/`. This manifest records physical moves and review decisions; it does not claim semantic audit of every schema.

| Previous Root | New Location | Action | Notes |
| --- | --- | --- | --- |
| `schema/` | `contracts/schema/` | moved | Source schema law and adjacent schema documentation moved with history preserved. |
| `schemas/` | `contracts/schema/` | merged | Validator-facing schema projections merged into `contracts/schema/`; filename conflicts were preserved under `contracts/schema/from-root-schemas/`. |
| `compat/` | `compat/` | review | Left in place because it contains Python compatibility implementation and shim code, not only contract definitions. |
| `locks/` | `locks/` | review | Left in place because it contains concrete deterministic pack lock artifacts, not only lockfile schemas. |
| `registry/` | none | absent | No root-level `registry/` was present during CONVERGE-06. |
| `registries/` | none | absent | No root-level `registries/` was present during CONVERGE-06. |
| `data/registries/` | `data/registries/` | review | Left in place because it is nested data/registry material outside the root-only CONVERGE-06 move scope. |

## Current Contract Classes

- `contracts/abi/`
- `contracts/schema/`
- `contracts/registry/`
- `contracts/protocol/`
- `contracts/capability/`
- `contracts/compatibility/`
- `contracts/stability/`
- `contracts/replay/`
- `contracts/repo/`
- `contracts/distribution/`
- `contracts/package/packs/`
- `contracts/install/`
- `contracts/instance/`
- `contracts/save/`
- `contracts/package/bundles/`
- `contracts/lock/`

## Conflicts

The root `schemas/README.md` collided with the moved `schema/README.md` target and was preserved at `contracts/schema/from-root-schemas/README.md`.

## References Updated

Active tooling, script, test, CMake, and GitHub automation references to root-level `schema/` and `schemas/` were updated to `contracts/schema/` where they referred to the moved roots.

## Material Not Moved

`compat/`, `locks/`, and `data/registries/` remain under review. They require file-level ownership inspection before any future movement.

## CONVERGE-09 Domain Split Note

CONVERGE-09 inspected root-level domain packages and moved Python implementation source to `game/domain/<domain>/`. The moved roots did not contain identified schema, registry, capability, protocol, content, docs, or test subsets during this pass.

Domain contract authority remains under:

- `contracts/schema/<domain>/`
- `contracts/registry/<domain>/`
- `contracts/capability/<domain>/`
- `contracts/protocol/<domain>/`

Domain implementation must stay under `game/domain/`, not `contracts/`.
