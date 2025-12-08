# Package Specification

The Domino/Dominium core now treats packages as filesystem-backed assets. The
in-memory registry mirrors what exists on disk and is rebuilt on every
`dom_core_create`.

## Roots
- Official/installed content lives under `dsys_get_path(DSYS_PATH_APP_ROOT)`.
- User-installed mods live under `dsys_get_path(DSYS_PATH_USER_DATA)`.
- All paths are relative to those roots and use forward slashes in descriptors.

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
