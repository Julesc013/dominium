Status: PROVISIONAL
Phase: CONVERGE-01
Supersedes: none
Superseded By: none
Stability: provisional

# Repository Ownership Rules

These rules explain the ownership model encoded in `contracts/repo/layout.contract.toml`. They do not authorize physical moves in CONVERGE-01.

## `contracts/`

Owns schemas, registries, protocols, capabilities, compatibility, stability, replay, ABI, repository layout, and distribution contracts.

`contracts/` must not contain generated package bytes, mutable runtime state, product entrypoints, or implementation convenience that silently changes schema law.

## `engine/`

Owns deterministic engine substrate only: portable mechanisms, public engine contracts, and engine-level tests.

`engine/` must not own OS GUI behavior, renderer state, platform calls as simulation inputs, product behavior, or game rule meaning.

## `game/`

Owns Dominium rules, domain process semantics, authority rules, world/economy/civilization logic, and game-facing domain implementation.

`game/` depends on engine contracts but must not place product shell behavior, platform adapters, generated dist output, or tool-only code inside domain truth.

## `runtime/`

Owns AppShell, platform adapters, render adapters, audio, input, network, storage, diagnostics, and UI adapters.

Runtime may host, adapt, observe, and present. Runtime does not own simulation truth, game law, domain semantics, or process authority.

## `apps/`

Owns thin product entrypoints and product-specific composition only.

If a product root contains AppShell logic, platform adapters, renderer backends, UI contracts, domain rules, schemas, registries, pack data, or docs, those parts require later split by ownership.

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
