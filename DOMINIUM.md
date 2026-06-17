Status: DERIVED
Last Reviewed: 2026-06-17
Supersedes: legacy top-level `DOMINIUM.md` product stub
Superseded By: none
Stability: provisional
Future Series: PUBLIC-DOCS
Replacement Target: long-lived public product overview derived from canon, contracts, and current status

# Dominium Product Overview

Dominium is the official game and product layer built on the Domino deterministic
substrate. It turns Domino's execution, ordering, replay, storage, and
ABI-facing boundaries into a governed simulation-game platform for authored
worlds, law, logistics, institutions, packs, tools, and projection surfaces.

This file is a public product overview. It is not canon. If it conflicts with
`docs/canon/constitution_v1.md`, `docs/canon/glossary_v1.md`, `AGENTS.md`,
active contracts, or `.aide/queue/current.toml`, the higher-authority artifact
wins.

## Product Positioning

Dominium is a deterministic, contract-governed simulation game and operating
environment. It is designed around explicit commands, lawful refusals,
capabilities, diagnostics, evidence, replay proof, and projection surfaces.

The product direction is not "a renderer owns the game." The product direction
is:

```text
lawful intent
  -> command
  -> capability and refusal checks
  -> deterministic process or service
  -> result, document, or snapshot
  -> diagnostics and evidence
  -> projection surface
```

A UI, renderer, Workbench panel, CLI, or agent tool should project that same
truth instead of creating separate product behavior.

## Domino And Dominium

| Name | Meaning |
|---|---|
| **Domino** | The reusable deterministic substrate: execution, ordering, storage, replay, ABI-facing boundaries, and engine mechanisms. |
| **Dominium** | The official game/product/domain layer: law targets, process meaning, authored content use, rule meaning, product composition, and user-facing surfaces. |

Domino provides the substrate. Dominium gives that substrate product meaning.

## Product Surfaces

| Surface | Role | Current public boundary |
|---|---|---|
| Client | Input, perception, and presentation shell. | Not a final playable release. |
| Server | Authoritative product composition and admin/headless surfaces. | Server authority remains governed by contracts and current narrow slices. |
| Launcher | Profiles, instances, compatibility, and launch orchestration. | Launch behavior must respect profiles, packs, contracts, and compatibility law. |
| Setup | Install, repair, rollback, and local product configuration. | Install/setup mutation must remain explicit and auditable. |
| Workbench | Validation, evidence, inspection, and later authoring workflows. | Broad Workbench UI remains blocked; only reviewed narrow slices are open. |
| Tools | Validators, codegen, migration, packaging, audit, and developer machinery. | Tools generate evidence or derived outputs unless a higher source promotes them. |

## What Exists Today

Dominium currently exists as a public repository with:

- C17/C++17 source roots and C-compatible ABI-facing public boundary policy
- product roots under `apps/`
- Domino substrate roots under `engine/`
- Dominium domain/game roots under `game/`
- runtime shell, platform, view, diagnostics, storage, input, audio, network,
and host integration under `runtime/`
- machine-readable contracts under `contracts/`
- authored content and pack surfaces under `content/`
- tests, validators, audits, and proof machinery under `tests/` and `tools/`
- repo governance, queue, and agent-maintenance surfaces under `.aide/` and
`AGENTS.md`

Current public status is maintained in `docs/STATUS.md`.

## What Does Not Exist Yet

Dominium should not be described as:

- a finished game
- a public release
- a production SDK
- a complete Workbench editor
- a completed renderer/native GUI product
- a broad gameplay implementation
- an arbitrary executable mod platform
- a system where planned architecture equals implemented behavior

The current queue explicitly keeps broad Workbench UI, runtime module loading,
provider runtime, package runtime, gameplay, renderer implementation, native
GUI, and release publication blocked.

## User And Developer Audiences

| Audience | Useful entrypoint |
|---|---|
| New reader | `README.md` |
| Product/architecture reader | this file, `docs/ARCHITECTURE.md` |
| Status reviewer | `docs/STATUS.md`, `.aide/queue/current.toml` |
| Roadmap reviewer | `docs/ROADMAP.md` |
| Contributor | `CONTRIBUTING.md`, `AGENTS.md` |
| Mod/content author | `MODDING.md`, `content/README.md`, `content/packs/README.md` |
| Agent or automation maintainer | `AGENTS.md`, `.aide/context/latest-task-packet.md` |

## Product Principles

1. **Determinism before presentation.** Product surfaces must not change
authoritative outcomes by presentation convenience.
2. **Process-only mutation.** Authoritative truth changes through lawful,
deterministic Process execution.
3. **Refusal is a first-class result.** Invalid, unsupported, or incompatible
actions refuse explicitly instead of falling back silently.
4. **Packs are data-first.** Optional content and capabilities are declared by
packs, contracts, registries, and compatibility law.
5. **Profiles beat mode flags.** Product variation should come from profiles,
law surfaces, bundles, and constraints.
6. **Evidence constrains claims.** Public docs should separate implemented,
planned, experimental, blocked, and not-currently-supported behavior.

## Key Product Docs

- Public front door: `README.md`
- Current status: `docs/STATUS.md`
- Architecture overview: `docs/ARCHITECTURE.md`
- Roadmap: `docs/ROADMAP.md`
- Documentation root: `docs/README.md`
- Canon index: `docs/architecture/CANON_INDEX.md`
- Canonical system map: `docs/architecture/CANONICAL_SYSTEM_MAP.md`
- Services and products: `docs/architecture/SERVICES_AND_PRODUCTS.md`
- Product shell contract: `docs/architecture/PRODUCT_SHELL_CONTRACT.md`
- Launcher contract: `docs/architecture/LAUNCHER_CONTRACT.md`
- Setup/installer contract: `docs/architecture/INSTALLER_CONTRACT.md`
- Tools contract: `docs/architecture/TOOLS_AS_CAPABILITIES.md`
- Directory/layout contracts: `contracts/repo/layout.contract.toml`,
`docs/repo/REPO_LAYOUT_TARGET.md`

## Maintenance Rule

When the product story changes, update the governing contract, queue, or audit
first. Then update `docs/STATUS.md`, `docs/ROADMAP.md`, and this public overview
as derived summaries. Do not convert future direction into current capability.
