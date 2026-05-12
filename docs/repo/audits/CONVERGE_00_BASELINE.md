Status: PROVISIONAL
Last Reviewed: 2026-05-12
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: REPO-CONVERGENCE
Replacement Target: CONVERGE-01 machine-readable layout contract and generated root inventory

# CONVERGE-00 Baseline — Repository Layout and Migration Preflight

## Purpose

This audit records the pre-convergence state of `julesc013/dominium` before any layout migration.

This pass is intentionally non-mutating:

- no directories moved
- no files deleted
- no build targets renamed
- no product ids changed
- no executable names changed
- no install ids changed
- no pack ids changed
- no virtual roots changed
- no CMake semantics changed

CONVERGE-00 exists to freeze the observable starting point for the later machine-readable layout contract, root inventory, move map, and non-blocking validator.

## Repository Baseline

Repository: `Julesc013/dominium`
Default branch: `main`
Baseline commit: `0406a0d188b399a8f5d3fb9119d25a91af9a6204`
Baseline commit message: `Merge branch 'main' of https://github.com/Julesc013/dominium`
Baseline author/committer as reported by GitHub connector: `codex`
Baseline commit timestamp: `2026-01-18T12:04:19Z`

Known branches observed during this audit:

- `main`
- `recovery/mega-13cb8ca7`

CONVERGE branch created for this audit:

- `converge/converge-00-baseline`

## Current Layout Diagnosis

The repository currently carries multiple physical-root concepts at top level. Known observed or referenced root-level concepts include:

```text
.github/
.vscode/
app/
appshell/
archive/
artifacts/
astro/
attic/
bundles/
chem/
client/
compat/
control/
core/
data/
diag/
dist/
docs/
electric/
engine/
field/
fields/
fluid/
game/
geo/
launcher/
legacy/
lib/
libs/
locks/
materials/
physics/
process/
profiles/
quarantine/
repo/
runtime/
schema/
schemas/
server/
setup/
thermal/
tools/
ui/
updates/
worldgen/
```

This list is a baseline diagnosis, not the final machine-readable inventory. CONVERGE-01 must generate a complete current-root inventory mechanically from the working tree and write it to:

```text
tools/migration/root_inventory.json
```

## Existing Empty Inventory

A pre-existing inventory file was observed:

```text
data/audit/repo_inventory.json
```

Its content on `main` is empty at the time of this audit. It must not be treated as authoritative current inventory.

CONVERGE-01 should either:

1. leave it as historical/legacy audit data, or
2. classify and migrate it under the new contract, probably to one of:

```text
archive/generated/
tools/migration/
docs/repo/audits/
```

The final destination must be decided by the layout contract, not ad hoc movement.

## Existing Layout Authority Conflict

The repo already contains multiple documents that claim or imply layout authority.

### `docs/architecture/ARCH_REPO_LAYOUT.md`

Current status header marks it as canonical, but its patch notes say the concrete top-level layout is stale relative to the real repository tree.

It still describes a layout with root-level product and contract/data folders such as:

```text
client/
server/
launcher/
setup/
tools/
libs/
data/
schema/
sdk/
legacy/
```

This document should be preserved as historical context but superseded for current layout authority by:

```text
contracts/repo/layout.contract.toml
```

### `docs/architecture/DIRECTORY_CONTEXT.md`

Current content calls itself the authoritative directory/layout contract. It also describes the older root layout with root-level product folders, `libs/`, `schema/`, `build/`, and `dist/`.

This creates direct authority conflict with the planned convergence model.

It should be patched during CONVERGE-01/02 to say that it is a legacy reference or derived explanation, not the machine-enforced layout authority.

### `docs/restructure/FUTURE_LAYOUT_PROPOSAL.md`

This document is a no-move planning artifact. It correctly requires:

- no semantic changes in move-only work
- compatibility shims before disruptive moves
- one subsystem per move
- stable product ids, executable names, pack ids, install ids, and virtual roots
- validation after every subsystem move

However, its proposed `/src/...` layout is not automatically accepted as final. CONVERGE-01 should preserve it as an input, not as binding target structure.

## Current README State

The root README is still marked likely out of date.

It describes the intended project model as:

- Dominium game on the Domino engine
- C89 deterministic engine
- C++98 native product applications
- Setup, Launcher, Client, Server, and Tools as native executable applications
- unified CLI for all applications
- expected TUI support
- native OS SDK GUIs for non-client products
- rendered cross-platform client GUI with multiple platforms/renderers

It also still presents current high-level architecture as:

```text
engine/
game/
client/
server/
repo/
tests/
tools/*x/
```

This is useful as historical/user-facing framing but should not remain the authoritative source of physical layout after CONVERGE-01/02.

## Existing Distribution and Install Doctrine

The repo already contains useful distribution/install doctrine that should be retained and consolidated rather than replaced.

### Dist tree

`docs/distribution/DIST_TREE_CONTRACT.md` defines:

```text
dist/pkg/<platform>/<arch>/
dist/sys/<platform>/<arch>/
dist/sym/<platform>/<arch>/
dist/res/
dist/cfg/
dist/redist/
dist/meta/
```

It states:

- `dist/pkg` is the primary shipping artifact surface.
- `dist/sys` is the realized install projection for local/CI use.
- symbols are never merged into runtime payload packages.

This doctrine is sound and should be integrated into a distribution layout contract.

### Virtual paths

`docs/appshell/VIRTUAL_PATHS.md` defines AppShell logical roots including:

```text
VROOT_BIN
VROOT_EXPORTS
VROOT_INSTALL
VROOT_INSTANCES
VROOT_IPC
VROOT_LOCKS
VROOT_LOGS
VROOT_PACKS
VROOT_PROFILES
VROOT_SAVES
VROOT_STORE
```

This is the correct foundation for physical layout projection.

Expected correction for CONVERGE-04:

```text
VROOT_LOCKS       should not remain one generic lock bucket.
store/locks/      deterministic content, pack, and capability locks
runtime/locks/    process and IPC locks
ops/transactions/ setup/update/rollback transaction state
```

### Install model

`docs/architecture/INSTALL_MODEL.md` says portable installs must be self-describing at the install root and contain:

```text
install.manifest.json
semantic_contract_registry.json
bin/
store/
instances/
saves/
```

This is compatible with the planned layout-projection model.

### Content and storage model

`docs/architecture/CONTENT_AND_STORAGE_MODEL.md` defines a canonical root layout with:

```text
bin/
store/
instances/
saves/
exports/
```

and CAS identity rules based on canonical SHA-256, not host paths or timestamps.

This should remain binding doctrine, but it should be unified with the layout contract and distribution projection contract.

## Existing Build and Governance Hooks

The root `CMakeLists.txt` already runs several boundary and hygiene checks, including but not limited to:

```text
scripts/verify_cmake_no_global_includes.py
scripts/verify_build_target_boundaries.py
tools/ci/arch_checks.py
scripts/ci/check_hygiene_scan.py
scripts/verify_ide_quarantine.py
scripts/verify_ui_shell_purity.py
scripts/verify_abi_boundaries.py
scripts/verify_docs_sanity.py
```

The current CMake also exposes platform and renderer backend options, including:

```text
DOM_PLATFORM = sdl2 | win32 | win32_headless | null | posix_headless | posix_x11 | posix_wayland | cocoa

DOM_BACKEND_SOFT
DOM_BACKEND_NULL
DOM_BACKEND_DX9
DOM_BACKEND_DX11
DOM_BACKEND_DX12
DOM_BACKEND_GL1
DOM_BACKEND_GL2
DOM_BACKEND_GL4
DOM_BACKEND_VK1
DOM_BACKEND_METAL
DOM_BACKEND_VECTOR2D
```

These are downstream of layout convergence. They should not drive physical layout decisions before contracts and boundary checks are stabilized.

## CONVERGE Target Direction

The proposed target source-root allowlist is:

```text
apps/
engine/
game/
runtime/
contracts/
content/
docs/
tests/
tools/
scripts/
cmake/
external/
release/
archive/
```

Controlled optional roots:

```text
sdk/
examples/
```

Allowed project/tooling roots and files should include:

```text
.github/
.vscode/
.aide/
AGENTS.md
CLAUDE.md
CMakeLists.txt
CMakePresets.json
CONTRIBUTING.md
DOMINIUM.md
GOVERNANCE.md
LICENSE.md
README.md
SECURITY.md
VERSION_*
```

Existing `repo/` must be classified and migrated. It should not become a new permanent top-level authority bucket unless the layout contract explicitly permits it.

## Planned Ownership Model

### `contracts/`

Authority for:

```text
abi/
schemas/
registries/
protocols/
capabilities/
compatibility/
stability/
replay/
repo/
distribution/
```

### `engine/`

Deterministic simulation substrate only.

Expected ownership:

```text
fields/
processes/
assemblies/
law/
deterministic/
include/
src/
tests/
```

Must not depend on:

```text
apps/
runtime/ui/
platform GUI APIs
renderer APIs
host paths
```

### `game/`

Dominium-specific rules and simulation semantics.

Expected ownership:

```text
domains/
rules/
authority/
world/
economy/
civilization/
tests/
```

### `runtime/`

Host-facing adapters and product runtime substrate.

Expected ownership:

```text
appshell/
platform/
render/
ui/
input/
audio/
network/
storage/
diagnostics/
```

Runtime may host and adapt. It must not own simulation truth.

### `apps/`

Thin product entrypoints:

```text
setup/
launcher/
client/
server/
tools/
```

Product semantics should not accumulate here.

### `content/`

Data and packs:

```text
packs/
profiles/
fixtures/
domain-data/
assets/
```

No mutable runtime store. No generated `dist`. No source-code behavior.

### `release/`

Release definitions, recipes, matrices, manifests.

No generated package bytes.

### `archive/`

Historical, legacy, quarantined, superseded, and generated historical material.

Expected substructure:

```text
archive/historical/
archive/legacy/
archive/quarantine/
archive/superseded/
archive/generated/
```

## Four-Way Domain Split Rule

Root-level domain folders must not be moved wholesale unless proven pure.

Each domain must be split by ownership:

| Domain Surface | Target Home |
| --- | --- |
| schemas / registries / capabilities | `contracts/...` |
| implementation / process semantics | `game/domains/<domain>/` |
| data / packs / fixtures | `content/...` or `tests/fixtures/...` |
| documentation | `docs/domains/<domain>/` |
| deterministic/replay tests | `tests/...` or domain-local tests |

Example:

```text
geo/schemas/     -> contracts/schemas/geology/
geo/registries/  -> contracts/registries/geology/
geo/src/         -> game/domains/geology/
geo/fixtures/    -> content/fixtures/geology/ or tests/fixtures/geology/
geo/docs/        -> docs/domains/geology/
geo/tests/       -> tests/determinism/geology/ or game/domains/geology/tests/
```

## Immediate Follow-Up: CONVERGE-01/02

The next work item should be:

```text
CONVERGE-01/02 — Layout Contract, Audit, and Stale Authority Supersession
```

Required deliverables:

```text
contracts/repo/layout.contract.toml
contracts/repo/layout.schema.json
tools/validators/check_repo_layout.py
tools/migration/root_inventory.json
tools/migration/root_move_map.json
docs/repo/REPO_LAYOUT_TARGET.md
docs/repo/OWNERSHIP_RULES.md
docs/repo/DOMAIN_SPLIT_RULES.md
docs/repo/ROOT_FILE_POLICY.md
```

Patch status/cross-reference language in:

```text
docs/architecture/ARCH_REPO_LAYOUT.md
docs/architecture/DIRECTORY_CONTEXT.md
docs/restructure/FUTURE_LAYOUT_PROPOSAL.md
README.md
```

Validator behavior:

- audit-only by default
- strict mode only with `--strict`
- classify each current top-level root
- write/update `tools/migration/root_inventory.json`
- read `tools/migration/root_move_map.json` if present
- print findings
- exit 0 by default

## CONVERGE Sequence

```text
CONVERGE-00  sync main, clean tree, baseline snapshot
CONVERGE-01  layout contract + non-blocking audit
CONVERGE-02  stale layout authority supersession + root allowlist policy
CONVERGE-03  complete inventory and move map
CONVERGE-04  distribution/install/media projection contract
CONVERGE-05  archive/attic/legacy/quarantine convergence
CONVERGE-06  contracts/schema/registry/compat convergence
CONVERGE-07  runtime/AppShell/platform/render/UI convergence
CONVERGE-08  product entrypoints into apps/
CONVERGE-09  domain split into contracts/game/content/docs/tests
CONVERGE-10  blocking layout validator
CONVERGE-11  product/platform/render/native/toolchain/package matrices
CONVERGE-12  stale-doc and cross-reference cleanup
```

## Boundary Conditions

CONVERGE work must preserve:

- deterministic engine behavior
- semantic contract pinning
- AppShell virtual-root semantics
- product ids
- executable names
- install ids
- pack ids
- save/instance compatibility
- `.dompkg` semantics
- build output identity unless explicitly revised

## Current Decision

The correct next move is not a physical restructure.

The correct next move is a machine-readable layout authority layer with non-blocking audit enforcement.

This prevents the repo from accumulating another prose-only plan while preserving build safety.
