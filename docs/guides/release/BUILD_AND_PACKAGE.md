Status: DERIVED
Last Reviewed: 2026-02-01
Supersedes: none
Superseded By: none

# Build and Package (Release)

Doc Version: 1

This document provides exact commands to build the repo and generate packaging artifacts from the canonical `artifact_root/` layout.

## 1) Build

Build with the standard preset:

```
cmake --build --preset debug
```

To enable packaging helper targets (`dominium_stage_dist`, `dominium_msi`, etc.), configure with `DOMINIUM_ENABLE_PACKAGING=ON` before building:

```
cmake --preset debug -DDOMINIUM_ENABLE_PACKAGING=ON
cmake --build --preset debug
```

## 2) Assemble canonical artifact_root/

Windows (cmd):

```
set SOURCE_DATE_EPOCH=946684800
python scripts\packaging\pipeline.py assemble --build-dir build\Debug --out dist\artifacts\dominium-0.1.0 --version 0.1.0 --manifest-template assets\setup\manifests\product.template.json --reproducible
```

macOS/Linux (bash):

```
export SOURCE_DATE_EPOCH=946684800
python scripts/packaging/pipeline.py assemble --build-dir build/debug --out dist/artifacts/dominium-0.1.0 --version 0.1.0 --manifest-template assets/setup/manifests/product.template.json --reproducible
```

## 3) Portable archives (zip/tar.gz)

```
python scripts/packaging/pipeline.py portable --artifact dist/artifacts/dominium-0.1.0 --out dist/portable --version 0.1.0 --reproducible
```

## 4) Windows MSI / bootstrapper

Requirements: WiX `candle` + `light`.

Pipeline (artifact_root → MSI / bootstrapper):

```
python scripts/packaging/pipeline.py windows --artifact dist/artifacts/dominium-0.1.0 --out dist/windows --version 0.1.0 --reproducible
python scripts/packaging/pipeline.py windows --artifact dist/artifacts/dominium-0.1.0 --out dist/windows --version 0.1.0 --bootstrapper --reproducible
```

CMake targets (requires `DOMINIUM_ENABLE_PACKAGING=ON`):

```
cmake --build --preset debug --target dominium_stage_dist
cmake --build --preset debug --target dominium_msi
cmake --build --preset debug --target dominium_bundle
```

## 5) macOS PKG / DMG

Requirements: `bash`, `pkgbuild`, `productbuild`, `hdiutil` (optional `codesign`).

```
python scripts/packaging/pipeline.py macos --artifact dist/artifacts/dominium-0.1.0 --out dist/macos --version 0.1.0 --identifier com.dominium.game --reproducible
```

## 6) Linux tar / deb / rpm

Requirements: `dpkg-deb` for `.deb`, `rpmbuild` for `.rpm`, `bash` for `.run`.

```
python scripts/packaging/pipeline.py linux --artifact dist/artifacts/dominium-0.1.0 --out dist/linux --version 0.1.0 --reproducible
python scripts/packaging/pipeline.py linux --artifact dist/artifacts/dominium-0.1.0 --out dist/linux --version 0.1.0 --build-deb --build-rpm --reproducible
```

## 7) Steam depot staging (mock ok)

```
python scripts/packaging/pipeline.py steam --artifact dist/artifacts/dominium-0.1.0 --out dist/steam --version 0.1.0 --appid 0 --depotid 0 --reproducible
```

## 8) Packaging validation test

```
ctest --preset debug -R dsu_packaging_validation_test
```