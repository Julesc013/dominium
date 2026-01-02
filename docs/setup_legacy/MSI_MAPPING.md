# MSI Mapping (Canonical)

## Identity and versioning

- UpgradeCode: `{5E6234E6-0C7F-4D37-8DE8-4B79CF6C9445}` (stable across all releases)
- ProductCode: derived from `MD5("dominium-msi-<version>-<arch>")`
- PackageCode: derived from `MD5("dominium-msi-<version>-<arch>-<build_id>")`
- Version: `Major.Minor.Patch` from `DOM_PROJECT_SEMVER`
- Major upgrades replace older versions; side-by-side only if a distinct UpgradeCode is explicitly declared.

## Feature and component mapping

- MSI Feature table entries are 1:1 with manifest component IDs (`components[].component_id`).
- MSI Component table contains only:
  - Setup Core binary (`.dsu\artifact_root\setup\dominium-setup.exe`)
  - manifest files (`.dsu\artifact_root\setup\manifests\*`)
  - policy files (`.dsu\artifact_root\setup\policies\*`)
  - payload container files (`.dsu\artifact_root\payloads\*`)
- All other files are installed by Setup Core.

## Property -> invocation mapping

- `DSU_OPERATION` -> `operation`
- `DSU_SCOPE` -> `scope`
- `DSU_PLATFORM` -> `platform_triple`
- `INSTALLDIR` -> `install_roots[0]`
- `DSU_DETERMINISTIC` -> `policy_flags.deterministic`
- `DSU_OFFLINE` -> `policy_flags.offline`
- `DSU_ALLOW_PRERELEASE` -> `policy_flags.allow_prerelease`
- `DSU_LEGACY_MODE` -> `policy_flags.legacy_mode`
- `DSU_UI_MODE` -> `ui_mode` (UILEVEL < 5 forces `cli`)
- `DSU_FRONTEND_ID` -> `frontend_id`
- `ADDLOCAL` -> `selected_components` (install/upgrade/repair)
- `REMOVE` -> `excluded_components` (install/upgrade/repair)
- `REMOVE=ALL` -> `selected_components` (uninstall)

## Defaults and fallbacks

- If `DSU_OPERATION` is empty:
  - `REMOVE=ALL` -> uninstall
  - `REINSTALL` set -> repair
  - `UPGRADINGPRODUCTCODE` set -> upgrade
  - else install
- If `DSU_SCOPE` is empty:
  - `ALLUSERS=1` -> system
  - `MSIINSTALLPERUSER=1` -> user
  - else user

## Invocation payload

- Default path: `%TEMP%\dominium-invocation.tlv`
- Override path: `DSU_INVOCATION_PATH`
- Invocation digest is logged in the MSI log by `InvokeSetupCore`.

## UI and install level

- `DSU_INSTALL_MODE=quick` sets `INSTALLLEVEL=1` (default selection)
- `DSU_INSTALL_MODE=custom` sets `INSTALLLEVEL=200` (show feature tree)
