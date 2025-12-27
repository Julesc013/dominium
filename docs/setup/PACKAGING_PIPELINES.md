# Packaging Pipelines (Plan S-8)

This document describes the **distribution & packaging pipelines** that transform build outputs into installable artifacts.
This phase produces **artifacts**, not install logic.

## Rules (locked)

- Packages embed **Setup Core** (`dominium-setup`) + **manifests** + **payloads**.
- Packages must not embed install decisions or logic beyond invoking `dominium-setup`.
- Installers generate `dsu_invocation` at install time; packaging does not encode logic.
- The same `product.dsumanifest` is embedded across all channels for a given platform build (MSI, PKG, deb/rpm, Steam).
- Canonical layout is deterministic and used by all wrappers (see `docs/setup/ARTIFACT_LAYOUT.md`).
- Offline-first: no downloads or network calls at install time unless explicitly configured.

## Build entrypoints

The repo provides a wrapper `Makefile` with these targets:

- `make package-portable`
- `make package-windows`
- `make package-macos`
- `make package-linux`
- `make package-steam`

All targets:

1. Assemble the canonical `artifact_root/` layout
2. Validate manifest ↔ payload consistency
3. Compute and record digests (`setup/artifact_manifest.json`, `setup/SHA256SUMS`)
4. Produce channel artifacts under `dist/`

## Script entrypoints (CI-friendly)

The repo also ships lightweight wrappers:

- Windows: `scripts/setup/build_packages.bat`
- POSIX: `scripts/setup/build_packages.sh`

Default usage (portable only):

```
scripts/setup/build_packages.bat build\debug 0.1.0
scripts/setup/build_packages.sh build/debug 0.1.0
```

These wrappers call:

```
python scripts/packaging/pipeline.py assemble --build-dir <build_dir> --out dist/artifacts/dominium-<version> --version <version> --manifest-template assets/setup/manifests/product.template.json
python scripts/packaging/pipeline.py portable --artifact dist/artifacts/dominium-<version> --out dist/portable --version <version>
```

Exit code is `0` on success; non-zero indicates packaging failure.

## Variables

`make` variables (override as needed):

- `BUILD_DIR` (required): CMake build directory containing `dominium-setup`, `dominium-launcher`, `dominium_game`
- `VERSION` (required): `x.y.z` version used in output filenames and `docs/VERSION`
- `MANIFEST_TEMPLATE`: manifest JSON template used to generate `setup/manifests/product.dsumanifest`
- `DIST_DIR`: output root (default: `dist`)
- `REPRODUCIBLE=1`: strict mode (requires `SOURCE_DATE_EPOCH`)

## Reproducibility

Strict reproducible mode:

```
SOURCE_DATE_EPOCH=946684800 REPRODUCIBLE=1 make package-portable
```

Rebuild verification:

- Compare `sha256` of the produced archives (byte-identical)
- Compare `setup/artifact_manifest.json` → `layout_sha256` (layout digest)

The canonical portable archives are built with deterministic settings (see `scripts/packaging/make_deterministic_archive.py`).

## Integrity records

Each assembled `artifact_root/` contains:

- `setup/artifact_manifest.json`: version + toolchain identifiers + manifest digest + file digests + `layout_sha256`
- `setup/SHA256SUMS`: `sha256  relative/path` list (does not list itself)

## Implementation

The build pipelines are implemented by:

- `scripts/packaging/pipeline.py` (assemble + package commands)
- `scripts/packaging/dsumanifest.py` (compile manifest JSON → `*.dsumanifest`)
- `scripts/packaging/make_deterministic_archive.py` (deterministic ZIP/tar.gz)

## See also

- `docs/setup/ARTIFACT_LAYOUT.md`
- `docs/setup/REPRODUCIBLE_BUILDS.md`
