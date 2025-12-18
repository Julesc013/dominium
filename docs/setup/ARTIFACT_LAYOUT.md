# Canonical Artifact Layout (Plan S-8)

This document locks the **canonical on-disk layout** used by all distribution channels
before platform wrapping (MSI/EXE, PKG/DMG, deb/rpm, Steam depots).

The canonical layout is referred to as `artifact_root/`.

## Goals

- Single layout for all channels (channel wrappers add metadata, not structure).
- Paths referenced by `*.dsumanifest` payload entries are **relative to** `artifact_root/`.
- Hashing and reproducibility operate over this layout.
- Offline-first: installers must not require network access at install time unless explicitly configured.

## Layout (locked)

```
artifact_root/
  setup/
    dominium-setup            (Setup Core CLI binary)
    manifests/
      product.dsumanifest     (canonical product manifest)
    policies/
      default.policy          (optional; deterministic)
  payloads/
    launcher/
    runtime/
    tools/
    packs/
  docs/
    LICENSE
    README
    VERSION
```

### Notes

- **No platform-specific paths** appear inside `artifact_root/` (no `Program Files`, `/Applications`, etc).
- Filenames may vary by build host (e.g. Windows may produce `dominium-setup.exe`); packaging pipelines must
  normalize into the canonical name/location in `artifact_root/` before wrapping.
- Channel wrappers must embed `artifact_root/` *as-is*.
- The `policies/default.policy` file is optional; if present it must be deterministic (no timestamps, no hostnames).

## Hashing rules

Hashing is computed over `artifact_root/` using **relative paths** with `/` separators.
Build pipelines must:

- enumerate files deterministically (lexicographic path order)
- compute `sha256` over file contents
- record digests in an artifact-manifest file alongside toolchain identifiers

The digest record must exclude any self-referential digest files (e.g. a `SHA256SUMS` file listing itself).

## Verification

Given an extracted/installed `artifact_root/`:

- `setup/manifests/product.dsumanifest` must validate and be internally consistent
- every payload referenced by the manifest must exist under `payloads/`
- payload digests recorded in the manifest must match the on-disk payload bytes

