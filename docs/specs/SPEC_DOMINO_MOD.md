Status: DERIVED
Last Reviewed: 2026-02-01
Supersedes: none
Superseded By: none

--------------------------------
OWNERSHIP & RESPONSIBILITY
--------------------------------
ENGINE:
- Deterministic primitives and invariants defined by this spec.
- Implementation lives under `engine/` (public API in `engine/include/`).

GAME:
- Rules, policy, and interpretation defined by this spec.
- Implementation lives under `game/` (rules/content/ui as applicable).

TOOLS:
- Authoring/inspection utilities described here.
- Implementation lives under `tools/` (including shared tool runtime).

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
# Content + Mod API (domino_mod)

`include/domino/mod.h` provides the shared registry/instance surface used across products.

## Plugin ABI (dom_mod_* and launcher_ext)
- Engine plugins export `dom_mod_vtable` (versioned struct) from `dom_mod_main`; `dom_mod_api` injects `dom_core`, event bus, and package registry pointers. Loader helpers (`dom_mod_load/dom_mod_get_vtable/dom_mod_unload`) are stubbed for now.
- Launcher extensions export `dom_launcher_ext_v1` via a symbol like `dom_get_launcher_ext_v1()`; hooks include `on_launcher_start`, `on_register_views`, `on_action(action_id,payload)`, and optional `on_build_canvas(inst, canvas_id, dom_gfx_buffer*)` for custom canvases. Helpers `dom_launcher_ext_register/count/get` live in `domino/mod.h`.
- All ABI structs start with `struct_size`/`struct_version` for compatibility; implementations remain no-ops until the runtime hooks are filled in.

## Shared content model
- `domino_package_registry` scans `data_root` and `user_root` for mods/packs using `domino_sys_dir_*`; manifests supply `id`, `version`, and `kind`.
- `domino_instance_desc` holds a product id/version plus enabled mods/packs.
- `domino_instance_resolve` checks that every requested mod/pack exists in the registry; future passes extend this into full dependency resolution.
- Setup, launcher, tools, and the game all consume the same registry/instance types to stay version-agnostic.

## Launcher behaviour
- Registry load: `domino_package_registry_scan_roots` over `domino_sys_paths.data_root` and `.user_root`.
- Instance discovery: `state/instances/` scanned for `*.instance.toml` (or `instance.toml` inside subdirs), parsed via `domino_instance_load`.
- Compatibility: `domino_instance_resolve` drives the "compatible" flag shown in views before a launch attempt.

## Launcher integration and launcher-target mods
- `kind` and `target` decide whether a package applies to the game, the launcher, or both; launcher builds its registry from any package whose `target` includes `launcher`.
- Launcher-facing compatibility lives in `[compat]` (`launcher_id`, `launcher_range`, `launcher_content_api`, `launcher_ext_api`).
- Optional `[launcher]` tables let packages declare UI hooks:
  - `enabled_by_default` flag to opt-in/out a launcher feature.
  - `[[launcher.view]]` entries describing views/tabs (`id`, `label`, `kind`, `priority`, `script_entry`) that are surfaced through the launcher view registry.
- Built-in views (instances/mods/packs/servers/accounts/tools) are compiled into the launcher; mod views attach through the same registry and, later, the extension API.

## Tools
- Reference tool `tools/dominium_modcheck` builds the registry and resolves a minimal instance per mod to surface missing dependencies or malformed manifests without running the game.

## Next steps
- Define deterministic mod manifests (deps/optional deps/content kinds).
- Extend resolver to handle dependency graphs, version ranges, and content categories.