# Contracts Root

Status: PROVISIONAL
Phase: CONVERGE-06
Supersedes: root-level `schema/` and `schemas/` as active schema roots
Superseded By: none
Stability: provisional

`contracts/` is the canonical source repository root for machine-readable, version-pinned, and compatibility-sensitive authority surfaces.

This root owns schemas, registries, protocols, capabilities, compatibility rules, stability rules, replay and proof contracts, ABI contracts, repo layout contracts, distribution projection contracts, pack contracts, install contracts, instance contracts, save contracts, bundle contracts, and deterministic lockfile contract definitions.

## Belongs Here

- `abi/`: public ABI and interface descriptions.
- `schemas/`: source schemas and validation schema families.
- `registries/`: registry definitions and registry schemas, not mutable runtime registry state.
- `protocols/`: protocol definitions, handshakes, IPC/network protocol contracts.
- `capabilities/`: capability negotiation, baselines, and feature/capability tables.
- `compatibility/`: compatibility, deprecation, pack/install compatibility, and refusal rules.
- `stability/`: stability tags, classes, and policy contracts.
- `replay/`: replay, proof, and reproducibility bundle format contracts.
- `repo/`: source repository layout and root allowlist contracts.
- `distribution/`: distribution, install, media, package, bundle, and runtime projection contracts.
- `packs/`, `install/`, `instances/`, `saves/`, and `bundles/`: package, install, instance, save, and bundle contract families.
- `locks/`: deterministic lockfile schemas and contract definitions only.

## Does Not Belong Here

`contracts/` must not contain product entrypoints, runtime mutable state, generated package bytes, runtime lock artifacts, game implementation, domain Process logic, or authored content payloads.

Human explanation belongs in `docs/`. Documentation may reference this root, but prose under `docs/` does not override machine-readable contracts here.

Runtime implementation belongs in `runtime/`. Runtime may consume contract definitions, but mutable runtime state, process locks, IPC locks, and transient files do not belong under `contracts/`.

Game/domain implementation belongs in `game/`. Domain schemas and registries may live here, but authoritative domain logic and Process execution do not.

Authored packs, profiles, fixtures, datasets, and assets belong under `content/` or their transitional roots until later convergence.

## Lock-Root Split

- `contracts/lock/`: deterministic lockfile schemas and contract definitions.
- `store/locks/`: deterministic content, pack, capability, and compatibility lock artifacts in install/runtime projections.
- `runtime/locks/`: process, IPC, and transient runtime locks.
- `ops/transactions/`: setup, update, rollback plans, stages, commits, and rollback records.

Do not place mutable runtime lock files under `contracts/`.

## Retired Roots

Root-level `schema/` and `schemas/` were retired in CONVERGE-06. Retained schema material now lives under `contracts/schema/`.

## CONVERGE-09 Domain Contract Note

CONVERGE-09 moved root-level domain implementation packages under `game/domain/`. No domain schema, registry, capability, or protocol subsets were identified inside those moved roots during the safe split.

Future domain contracts must live under the appropriate contract class, such as `contracts/schema/<domain>/`, `contracts/registry/<domain>/`, `contracts/capability/<domain>/`, or `contracts/protocol/<domain>/`. Domain implementation does not belong in `contracts/`.
