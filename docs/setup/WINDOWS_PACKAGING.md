# Windows Packaging (MSI Canonical)

## Outputs

- `dist/installers/windows/msi/DominiumSetup-<version>-x86.msi`
- `dist/installers/windows/msi/DominiumSetup-<version>-x64.msi`
- EXE parity installer planned (not implemented in this prompt)

## Tooling

Required (installed separately; not downloaded by the pipeline):

- WiX Toolset 3.x or 4.x (`candle`, `light`) on `PATH`
- Python 3
- CMake + MSVC

## Build

From the repo root:

```
cmake -S . -B build/msvc-x86 -DDOM_PROJECT_SEMVER=x.y.z
cmake -S . -B build/msvc-x64 -DDOM_PROJECT_SEMVER=x.y.z
cmake --build build/msvc-x86 --target msi-x86
cmake --build build/msvc-x64 --target msi-x64
```

Cross-arch inputs are configured via CMake cache:

- `DOMINIUM_MSI_BUILD_DIR_X86` / `DOMINIUM_MSI_BUILD_DIR_X64`
- `DOMINIUM_MSI_CA_X86` / `DOMINIUM_MSI_CA_X64` (InvokeSetupCore DLL per arch)

Artifacts land in `dist/installers/windows/msi/`.

## MSI behavior

The MSI:

- installs only Setup Core and payload containers into `INSTALLDIR\.dsu\artifact_root`
- maps MSI properties and tables to `dsu_invocation` fields
- writes the invocation payload and runs `dominium-setup apply --invocation <payload>`
- contains no additional install logic

See `docs/setup/MSI_MAPPING.md` for the mapping contract.

## Silent install

Examples:

- Silent: `msiexec /i DominiumSetup-x.y.z-x64.msi /qn DSU_SCOPE=user`
- Passive: `msiexec /i DominiumSetup-x.y.z-x64.msi /passive DSU_SCOPE=system`

## Determinism notes

Determinism is achieved by:

- staging a deterministic `artifact_root/`
- deterministic GUID generation in CMake (`_dom_msi_guid`)
- fixed `SOURCE_DATE_EPOCH` in reproducible mode

WiX itself must be a stable version in CI to guarantee byte-identical MSI outputs.

## Sources

- WiX authoring: `source/dominium/setup/installers/windows/msi/wix`
- WiX generator: `source/dominium/setup/installers/windows/msi/cmake/generate_msi_wix.py`
- Pipeline entry: `scripts/packaging/pipeline.py` (`assemble`)
