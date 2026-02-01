Status: DERIVED
Last Reviewed: 2026-02-01
Supersedes: none
Superseded By: none

--------------------------------
OWNERSHIP & RESPONSIBILITY
--------------------------------
ENGINE:
- None. Engine provides generic primitives only if referenced.

GAME:
- Rules, policy, and interpretation defined by this spec.
- Implementation lives under `game/` (rules/content/ui as applicable).

TOOLS:
- None. Tools may only consume public APIs if needed.

SCHEMA:
- None (no canonical schema formats defined here).

FORBIDDEN:
- No launcher/setup orchestration logic in engine or game.
- No engine internal headers exposed outside engine targets.
- No game rules or policy implemented inside engine primitives.

DEPENDENCIES:
- Engine -> libs/ and schema/ only (never game/launcher/setup/tools).
- Game -> engine public API and schema/ only.
- Tools -> engine public API, game public API, and schema/ only.
- Launcher/Setup (if applicable) -> libs/contracts + schema (launcher may also use engine public API).
--------------------------------
# Dominium Common Layer

## Purpose
- Bridges the C89 Domino engine with C++98 Dominium products (game, launcher, setup, tools).
- Centralizes instance management, content selection, and deterministic engine bootstrap without leaking backend details into products.
- Provides stable helpers that sit on top of Domino registries rather than duplicating engine systems.

## Directory Model
- Repository roots are anchored to `DOMINIUM_HOME`.
- Standard layout:
  - `repo/products/` – packaged product manifests.
  - `repo/packs/` – content packs by id/version.
  - `repo/mods/` – mods by id/version.
  - `instances/` – per-instance roots.
  - `temp/` – scratch space for tools.
- Paths are resolved deterministically and are independent of platform-specific separators.

## dom_paths
- Resolves the standard repository/instance/temp directories from a supplied `DOMINIUM_HOME`.
- Provides minimal string-only path joining to avoid platform-specific APIs.
- `file_exists` / `dir_exists` are thin stubs over `dsys` file APIs; they intentionally avoid direct OS calls.

## dom_instance
- `InstanceInfo` models persistent instance metadata: ids, world seed/size/range, active packs/mods, suite/core versions, and last-used product markers.
- Load/save uses a simple TLV container for deterministic, forward-compatible storage; unknown tags are ignored on load.
- Serialization is intentionally conservative: only stable fields are written, leaving room for forward schema growth.
- Pack/mod reference lists are canonical: sorted by `(id, version)` and deduped.
  Producers MUST preserve this ordering when writing instance files so pack/mod
  load order is deterministic.

## dom_packset
- Resolves pack/mod TLV payloads for an instance in deterministic order:
  - Packs: `repo/packs/<id>/<version>/pack.tlv` (fallback `pack.bin`).
  - Mods:  `repo/mods/<id>/<version>/mod.tlv` (fallback `mod.bin`).
- Loads TLV blobs into memory and exposes them for the content loader.
- Dependency/conflict resolution is not implemented in this pass. Contract:
  - Pack/mod lists provided by `dom_instance` MUST already be canonicalized
    (sorted by stable key, deduped) before `dom_packset` loads them.
  - Missing packs/mods are hard errors (no implicit fallback search beyond
    `*.tlv` → `*.bin` in the same version directory).

## dom_session
- Owns the runtime bridge to Domino:
  - Initializes the selected `dsys`/`dgfx` backends (headless/TUI safe).
  - Registers content schemas, loads packs/mods via Domino’s registries.
  - Creates the world from instance metadata and boots `dsim`.
  - Keeps pack/mod TLV memory alive for the lifetime of the session.
- `shutdown` tears down simulation, world, content, gfx, and system state deterministically.

## dom_compat
- Evaluates whether a product build can operate on a given instance.
- Rules (initial):
  - `prod.core_version < inst.core_version` → incompatible.
  - `prod.suite_version < inst.suite_version` → read-only.
  - `prod.suite_version > inst.suite_version` → limited (forward-compat behavior
    must be explicit; no silent upgrades).
  - Matching suite/core with required features → OK.
- Any compat extension must be explicit, versioned, and deterministic; silent
  reinterpretation of instance data is forbidden.

## Launcher/Setup/Tools
- **Launcher:** discovers products under `repo/products/`, instances under `instances/`, evaluates compatibility, and spawns the requested product (game/setup/tools) using `dsys_proc_spawn`. GUI/TUI shells stay inside DVIEW/DUI.
- **Setup:** CLI-first utility that installs/repairs/uninstalls/imports products, packs, and mods purely through `dom_paths`/`dsys` wrappers—no direct OS calls.
- **Tools:** utilities (e.g., `modcheck`) consume TLVs through the same schema registry as the engine; future editors will register via manifests so the launcher can list them.

## Compatibility model notes
- Launcher uses `dom_compat` to guard instance/product pairing: newer suite/core builds can run older instances in limited/read-only mode; older builds refuse newer core instances.
- Packs/mods/blueprints always flow through Domino registries—no product may bypass `d_content_load_*`—ensuring deterministic ordering and schema validation before world bootstrap.