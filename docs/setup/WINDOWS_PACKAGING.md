# Windows Packaging (MSI + Bootstrapper)

## Outputs

- `dist/windows/DominiumSetup-x.y.z.msi`
- `dist/windows/DominiumSetup-x.y.z.exe` (optional bootstrapper; produced by default via `make package-windows`)

## Tooling

Required (installed separately; not downloaded by the pipeline):

- WiX Toolset (`candle`, `light`) available on `PATH`

## Build

From the repo root:

```
SOURCE_DATE_EPOCH=946684800 REPRODUCIBLE=1 make package-windows BUILD_DIR=build/<your-build> VERSION=x.y.z
```

Artifacts land in `dist/windows/`.

## MSI behavior (design)

The MSI:

- installs the canonical `artifact_root/` layout into `INSTALLDIR`
- maps MSI properties to `dominium-setup` flags
- runs `dominium-setup plan` then `dominium-setup apply` via custom actions (no other install logic)

## MSI property → CLI mapping (locked)

Properties are stable and `Secure="yes"`:

- `DSU_SCOPE` → `--scope <portable|user|system>`
- `DSU_DETERMINISTIC` → global `--deterministic <0|1>`

Custom action command lines (conceptual):

- Plan:
  - `"dominium-setup.exe" --deterministic [DSU_DETERMINISTIC] plan --manifest "<...>/setup/manifests/product.dsumanifest" --op install --scope [DSU_SCOPE] --out "<tmp>/dominium.dsuplan"`
- Apply:
  - `"dominium-setup.exe" --deterministic [DSU_DETERMINISTIC] apply --plan "<tmp>/dominium.dsuplan"`

## Silent install

The MSI supports standard `msiexec` modes (examples):

- Silent: `msiexec /i DominiumSetup-x.y.z.msi /qn DSU_SCOPE=user`
- Passive: `msiexec /i DominiumSetup-x.y.z.msi /passive DSU_SCOPE=system`

## Determinism notes

Determinism is achieved by:

- staging a deterministic `artifact_root/`
- deterministic WiX IDs (product/package codes derived from version; file components derived from relative paths)
- fixed `SOURCE_DATE_EPOCH` in reproducible mode

WiX itself must be a stable version in CI to guarantee byte-identical MSI outputs.

## Sources

- WiX generator: `scripts/packaging/windows/generate_dominium_setup_wxs.py`
- Pipeline entry: `scripts/packaging/pipeline.py` (`windows` subcommand)

