# Windows MSI Installer (Canonical)

## Scope

- Windows NT 5.0+ (2000, XP, Vista, 7, 8, 10, 11)
- x86 and x64
- single MSI per architecture, fully self-contained (no downloads, no runtime deps)

## Outputs

- `dist/installers/windows/msi/DominiumSetup-<version>-x86.msi`
- `dist/installers/windows/msi/DominiumSetup-<version>-x64.msi`

## Build

Requirements (installed separately):

- WiX Toolset 3.x or 4.x (`candle`, `light`) on `PATH`
- Python 3
- CMake + MSVC

Configure MSI build inputs (cross-arch builds require two build dirs):

- `DOMINIUM_MSI_BUILD_DIR_X86` / `DOMINIUM_MSI_BUILD_DIR_X64`
- `DOMINIUM_MSI_CA_X86` / `DOMINIUM_MSI_CA_X64` (InvokeSetupCore DLL per arch)

Targets:

- `cmake --build <build-dir> --target msi-x86`
- `cmake --build <build-dir> --target msi-x64`

## Execution model

- MSI installs only Setup Core and static payload containers into `INSTALLDIR\.dsu\artifact_root`.
- MSI collects parameters, writes a TLV invocation payload, and invokes Setup Core once:
  - `dominium-setup apply --invocation <payload>`
- No other MSI install logic is permitted. Setup Core handles file mutation, shortcuts,
  and platform registrations based on the invocation payload.

## Wizard flow

1. Detect existing install (MSI product registration and Setup Core installed-state when present)
2. Maintenance UI when installed: Change / Repair / Remove
3. Operation selection: Install / Upgrade / Repair / Uninstall
4. Install mode: Quick or Custom
5. Scope selection: per-user / per-machine / portable
6. Component selection (Feature table == manifest components)
7. Summary, progress, completion

## Properties and command line

Core public properties:

- `DSU_OPERATION`, `DSU_SCOPE`, `DSU_PLATFORM`
- `DSU_DETERMINISTIC`, `DSU_OFFLINE`, `DSU_ALLOW_PRERELEASE`, `DSU_LEGACY_MODE`
- `DSU_UI_MODE`, `DSU_FRONTEND_ID`, `DSU_INVOCATION_PATH`
- `INSTALLDIR`

Feature and scope controls:

- `ADDLOCAL`, `REMOVE`
- `ALLUSERS`, `MSIINSTALLPERUSER`

## Silent and passive examples

Silent per-user install:

```
msiexec /i DominiumSetup-x.y.z-x64.msi /qn DSU_SCOPE=user INSTALLDIR="C:\Users\<user>\AppData\Local\Dominium"
```

Silent per-machine install:

```
msiexec /i DominiumSetup-x.y.z-x64.msi /qn DSU_SCOPE=system ALLUSERS=1 INSTALLDIR="C:\Program Files\Dominium"
```

Portable install:

```
msiexec /i DominiumSetup-x.y.z-x64.msi /qn DSU_SCOPE=portable INSTALLDIR="D:\DominiumPortable"
```

Passive UI:

```
msiexec /i DominiumSetup-x.y.z-x64.msi /passive DSU_SCOPE=user
```

## Repair and uninstall examples

Repair (reinstall all features):

```
msiexec /i DominiumSetup-x.y.z-x64.msi /qn REINSTALL=ALL REINSTALLMODE=vomus
```

Uninstall:

```
msiexec /x DominiumSetup-x.y.z-x64.msi /qn
```

## Enterprise usage notes

- Use `/l*v` to capture MSI logs (includes invocation digest).
- Set default properties with MST transforms or deployment tooling.
- Per-machine installs require elevation; MSI does not implement its own elevation flow.

## Parity guarantees

- MSI invocation payload digest must match the CLI export-invocation digest for the same inputs.
- MSI is the canonical Windows installer; the EXE parity installer must emit byte-identical invocation payloads.
