# Packaging Pipelines (Plan S-8)

This document describes the **distribution & packaging pipelines** that transform build outputs into installable artifacts.
This phase produces **artifacts**, not install logic.

## Rules (locked)

- Packages embed **Setup Core** (`dominium-setup`) + **manifests** + **payloads**.
- Packages must not embed install decisions or logic beyond invoking `dominium-setup`.
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

