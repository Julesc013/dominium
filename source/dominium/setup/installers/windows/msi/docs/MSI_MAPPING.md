# MSI Mapping (WiX Authoring)

This document mirrors `docs/setup/MSI_MAPPING.md` with details specific to the WiX sources
under `source/dominium/setup/installers/windows/msi/`.

## Identity rules

- UpgradeCode (stable): `{5E6234E6-0C7F-4D37-8DE8-4B79CF6C9445}`
- ProductCode: `MD5("dominium-msi-<version>-<arch>")`
- PackageCode: `MD5("dominium-msi-<version>-<arch>-<build_id>")`

## WiX source layout

- `wix/Product.wxs`: Product/Package/MajorUpgrade/Media
- `wix/Properties.wxs`: public `DSU_*` properties and scope defaults
- `wix/Directories.wxs`: `INSTALLDIR` and `.dsu\artifact_root` layout
- `wix/Features.wxs` + `Features.generated.wxi`: Feature table from manifest component IDs
- `wix/CustomActions.wxs`: only deferred executable CA (`InvokeSetupCore`)
- `wix/UI.wxs`: wizard flow and MSI dialogs

## CustomActionData contract

`SetInvokeSetupCore` populates key/value pairs consumed by `InvokeSetupCore`:

- `INSTALLDIR`, `DSU_OPERATION`, `DSU_SCOPE`, `DSU_PLATFORM`
- `DSU_DETERMINISTIC`, `DSU_OFFLINE`, `DSU_ALLOW_PRERELEASE`, `DSU_LEGACY_MODE`
- `DSU_UI_MODE`, `DSU_FRONTEND_ID`, `DSU_INVOCATION_PATH`
- `ADDLOCAL`, `REMOVE`, `UILEVEL`, `REINSTALL`, `UPGRADINGPRODUCTCODE`
- `ALLUSERS`, `MSIINSTALLPERUSER`

`InvokeSetupCore` writes the invocation payload to `DSU_INVOCATION_PATH`
(default `%TEMP%\dominium-invocation.tlv`) and runs:

```
dominium-setup --deterministic <0|1> apply --invocation <payload>
```

## Feature/component rules

- Feature IDs are manifest component IDs.
- Components only include Setup Core, manifest/policy files, and payload container files.
- Setup Core installs everything else.
