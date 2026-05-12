Status: PROVISIONAL
Phase: CONVERGE-08
Supersedes: none
Superseded By: none
Stability: provisional

# Repository Ownership Rules

These rules explain the ownership model encoded in `contracts/repo/layout.contract.toml`. Physical moves require an explicit CONVERGE phase and must stay within that phase scope.

## `contracts/`

Owns schemas, registries, protocols, capabilities, compatibility, stability, replay, ABI, repository layout, and distribution contracts.

`contracts/` must not contain generated package bytes, mutable runtime state, product entrypoints, or implementation convenience that silently changes schema law.

CONVERGE-06 moved root-level `schema/` and `schemas/` into `contracts/schemas/`. Root-level schema directories are retired and must not be recreated as active authority. Docs explain contract meaning, but docs do not override machine-readable contract definitions.

Runtime mutable state does not belong in `contracts/`. Store lock artifacts, process locks, IPC locks, package caches, setup/update transaction state, and rollback state are projection/runtime material, not contract source.

Content data does not belong in `contracts/` unless the file is a schema, registry definition, capability definition, protocol, or other explicit contract source.

Lock-root split:

- `contracts/locks/`: deterministic lockfile schemas and contract definitions.
- `store/locks/`: deterministic content, pack, capability, and compatibility lock artifacts.
- `runtime/locks/`: process, IPC, and transient runtime locks.
- `ops/transactions/`: setup, update, and rollback transaction state.

## `engine/`

Owns deterministic engine substrate only: portable mechanisms, public engine contracts, and engine-level tests.

`engine/` must not own OS GUI behavior, renderer state, platform calls as simulation inputs, product behavior, or game rule meaning.

## `game/`

Owns Dominium rules, domain process semantics, authority rules, world/economy/civilization logic, and game-facing domain implementation.

`game/` depends on engine contracts but must not place product shell behavior, platform adapters, generated dist output, or tool-only code inside domain truth.

## `runtime/`

Owns AppShell, platform adapters, render adapters, audio, input, network, storage, diagnostics, and UI adapters.

Runtime may host, adapt, observe, and present. Runtime does not own simulation truth, game law, domain semantics, or process authority.

CONVERGE-07 moved root-level `app/`, `appshell/`, `ui/`, and `diag/` under `runtime/`. Root-level runtime-adapter directories are retired when fully migrated and must not be recreated as active authority.

Runtime also must not own product semantics, product IDs, executable names, machine-readable contract law, generated runtime logs, process/IPC lock artifacts, caches, mutable stores, or package output. Runtime source belongs in `runtime/<subroot>/`; generated runtime projection material belongs to install/runtime layouts governed by the distribution contract.

Mixed runtime-adjacent roots such as `net/`, `control/`, and `core/` remain review roots. They must be split by file role before anything is bound to runtime, game, engine, contracts, or content ownership.

## `apps/`

Owns thin product entrypoints and product-specific composition only.

CONVERGE-08 moved root-level `client/`, `server/`, `setup/`, and `launcher/` under `apps/`. Those root-level product directories are retired and must not be recreated as active source authority.

`apps/` must not own runtime adapters, engine truth, game/domain law, schemas/contracts, content/packs, generated install/runtime/media output, or developer tooling. Product semantics flow through contracts, runtime, engine, game, and content layers. Product-specific UI shell code must remain thin and contract-bound.

If product-local material contains AppShell logic, platform adapters, renderer backends, UI contracts, domain rules, schemas, registries, pack data, or docs, those parts require later split by ownership rather than broad retention under `apps/`.

## `content/`

Owns authored packs, profiles, fixtures, datasets, assets, templates, and domain data.

`content/` must not contain generated dist output, mutable runtime stores, product behavior, or executable pack code.

## `release/`

Owns release definitions, package recipes, matrices, signing/release metadata, publication metadata, and release policy inputs.

`release/` must not contain generated package bytes or mutable install state.

## `tools/`

Owns developer, validation, migration, CI, code generation, review, and audit tools.

Runtime and product code must not depend on tools. Tools may inspect broad repo surfaces, but tool convenience does not create semantic authority.

## `archive/`

Owns historical, superseded, quarantined, generated-evidence, and legacy material.

Archive material is visible for provenance and archaeology. It must not silently become active source authority.

CONVERGE-05 made `archive/` the single archive-family ownership root. Root-level `attic/`, `legacy/`, and `quarantine/` are retired and their retained material lives under:

- `archive/historical/attic/`
- `archive/legacy/`
- `archive/quarantine/`

`archive/` does not own active source. Archived material must not become an active build input without an explicit reviewed exception. Quarantined material must remain visibly quarantined.

## CONVERGE-03 Ownership Surface Vocabulary

`tools/migration/root_inventory.json` uses the `ownership_surface` field to make later migration planning explicit. Allowed surfaces are:

- `apps`, `engine`, `game`, `runtime`, `contracts`, `content`, `docs`, `tests`, `tools`, `scripts`, `cmake`, `external`, `release`, and `archive` for target source ownership.
- `metadata` for allowed metadata directories and root coordination files.
- `generated` for build, release, or evidence outputs that are not source authority.
- `mixed_split_required` for roots that must be split across multiple owners.
- `unknown` for roots that need manual review before a target owner is chosen.

## Mixed Split Required

`mixed_split_required` means a root name is not enough evidence to move the directory wholesale. Later work must inspect file-level roles and split schemas, registries, implementation, content, docs, tests, generated outputs, and compatibility surfaces into their owning roots.

## Product Roots After Migration

Product roots under `apps/` must remain thin entrypoints and composition surfaces. AppShell logic, platform adapters, renderer backends, domain rules, schemas, registries, pack data, developer tools, and docs must be rehomed by ownership instead of carried into `apps/` as bulk product history.

## Runtime Roots After Migration

Runtime roots may host, adapt, observe, present, connect, persist, and diagnose. They must not own simulation truth, law, Process mutation, domain semantics, pack authority, or product identity.

## Content And Data Roots

Content ownership covers authored packs, profiles, fixtures, datasets, assets, templates, and domain data. Mixed roots such as `data/`, `packs/`, `bundles/`, and `templates/` require review because they may also contain registries, planning mirrors, generated evidence, or runtime-store assumptions.

## Generated And Ephemeral Roots

Generated roots are non-authoritative unless a stronger release or evidence contract says otherwise. `dist/`, `artifacts/`, `build/`, and `out/` must be treated as outputs or evidence, not source ownership.

## CONVERGE-06 Contract-Adjacent Review Roots

`compat/` and `locks/` remain root-level review items after CONVERGE-06:

- `compat/` contains Python implementation and shim code, so it cannot be moved wholesale into `contracts/compatibility/`.
- `locks/` contains concrete deterministic pack lock artifacts, so it cannot be moved wholesale into `contracts/locks/`.

Later phases must split these by file role before binding anything to contracts, runtime, store, or ops ownership.

## CONVERGE-09 Domain Ownership

CONVERGE-09 moved safe root-level domain implementation packages under `game/domains/`. The moved roots were implementation code only during inspection; domain schemas, registries, capabilities, protocols, authored content, docs, and tests remain governed by their own target roots.

Domain ownership surfaces are:

- `game/domains/<domain>/` for Dominium domain rules, deterministic implementation, process semantics, and domain engines.
- `contracts/schemas/<domain>/`, `contracts/registries/<domain>/`, `contracts/capabilities/<domain>/`, and `contracts/protocols/<domain>/` for machine-readable domain authority.
- `content/domain-data/<domain>/` and `content/packs/` for authored source data, datasets, and pack material.
- `docs/domains/<domain>/` for human-readable domain explanation.
- `tests/fixtures/<domain>/`, `tests/determinism/<domain>/`, `tests/regression/<domain>/`, and `tests/golden/<domain>/` for verification material.

Engine primitives remain an exception: universal deterministic substrate belongs under `engine/`, not under a domain merely because a domain uses it.

Domain code must not own runtime adapters, product entrypoints, generated runtime output, install/store state, or presentation state. It must preserve fixed-point truth discipline, named RNG streams, stable ordering, deterministic reductions, and process-only mutation.

## CONVERGE-10 Enforcement

Root ownership must match the layout contract and root allowlist. Deviations require an active entry in `contracts/repo/layout_exceptions.toml`.

Strict validators now block unexcepted ownership drift:

- product entrypoints outside `apps/`
- runtime adapters outside `runtime/`
- schemas, registries, or contracts outside `contracts/`
- domain roots outside the contracts/game/content/docs/tests split
- generated roots without generated policy or exception
- unknown root files or directories

Tools may inspect broadly for validation and migration planning. Runtime and product code must not depend on developer-only tooling under `tools/`.
