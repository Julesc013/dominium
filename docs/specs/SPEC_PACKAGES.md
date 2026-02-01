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
- None. Game consumes engine primitives where applicable.

TOOLS:
- Authoring/inspection utilities described here.
- Implementation lives under `tools/` (including shared tool runtime).

SCHEMA:
- Canonical formats and migrations defined here live under `schema/`.

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
# Package Specification

Packages are filesystem-backed containers for packs resolved by UPS. The
in-memory registry mirrors what exists on disk and is rebuilt on every
`dom_core_create`. Executables remain content-agnostic and may boot with zero
packages present.

## Roots
- Official/installed content lives under `dsys_get_path(DSYS_PATH_APP_ROOT)`.
- User-installed mods live under `dsys_get_path(DSYS_PATH_USER_DATA)`.
- All paths are relative to those roots and use forward slashes in descriptors.
- Setup/launcher tooling populates these roots. The package registry is a
  deterministic scanner over the on-disk layout; it does not define install or
  repair semantics.

## Layouts
### Official content
```
<app_root>/data/versions/<game_version>/<package_id>/
  manifest.ini
  content/...
```
- `<game_version>` is a stable string (e.g. `dev`, `1.0.0`). The current build
  uses `dev` as the default.
- These packages are treated as read-only; uninstalling them is rejected unless
  explicitly handled elsewhere.

### User mods
```
<user_data>/mods/<author>/<package_id>/
  manifest.ini
  content/...
```
- The `<author>/` segment is optional; bare `<user_data>/mods/<package_id>/`
  also works. Install will create the `<author>/` segment if provided.

## Manifest format (`manifest.ini`)
Plain text `key=value`, one per line. Unknown keys are ignored. Whitespace
around keys/values is trimmed. Supported keys:
- `id` – canonical package name/slug. Required.
- `kind` – one of `mod`, `content`, `product`, `tool`, `pack`. Defaults to
  `unknown`.
- `version` – semantic version string.
- `author` – free-form string. Used to place mods under `<author>/`.
- `deps` – comma-separated list of package ids (names). Resolved on load if the
  referenced package is present.
- `game_version_min` / `game_version_max` – compatible Dominium version bounds.
- `capabilities` – comma-separated capability ids declared by the pack.

Note: `manifest.ini` is container metadata. Pack manifests are versioned TLV
records handled by UPS (see `docs/specs/launcher/PACK_SYSTEM.md`).

## Registry behaviour
- On startup the core walks the official root (`data/versions/<game_version>`)
  and the user root (`mods/`), loading any directory that contains
  `manifest.ini`.
- Package ids are monotonically increasing integers assigned in sorted path
  order to keep behaviour deterministic.
- `install_path` points at the package root. `manifest_path` points at the
  manifest file. `content_root` points at the `content/` directory under the
  package root (created on install even if empty).
- Installing a mod copies the source directory (manifest + content) into
  `<user_data>/mods/<author>/<package_id>/` and registers it.
- Uninstall removes the registry entry and deletes the on-disk mod directory.
  Official packages under `<app_root>` are left intact.