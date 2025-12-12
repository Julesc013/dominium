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

## dom_packset
- Resolves pack/mod TLV payloads for an instance in deterministic order:
  - Packs: `repo/packs/<id>/<version>/pack.tlv` (fallback `pack.bin`).
  - Mods:  `repo/mods/<id>/<version>/mod.tlv` (fallback `mod.bin`).
- Loads TLV blobs into memory and exposes them for the content loader.
- Leaves dependency/conflict resolution as a TODO for later prompts.

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
  - `prod.suite_version > inst.suite_version` → limited (forward-compat TBD).
  - Matching suite/core with required features → OK.
- Future prompts will extend this with explicit compat profiles and feature checks.
