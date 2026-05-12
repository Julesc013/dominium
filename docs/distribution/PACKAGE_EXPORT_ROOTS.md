Status: PROVISIONAL
Phase: CONVERGE-04
Machine-Readable Authority: `contracts/distribution/layout.contract.toml`

# Package Export Roots

`.dompkg` artifacts export files into declared logical roots. They must not encode absolute host install paths.

Existing package-format inputs remain relevant:

- `docs/distribution/PKG_FORMAT.md`
- `docs/distribution/PKG_MANIFEST.md`
- `docs/distribution/PKG_INSTALL_AND_ROLLBACK.md`
- `schema/distribution/pkg_manifest.schema`

CONVERGE-04 adds the projection rule: package exports bind to logical roots first, then setup/install projects those roots physically.

## Target Roots

Allowed `target_root` values are:

- `install`
- `bin`
- `descriptors`
- `store`
- `packs`
- `profiles`
- `docs`
- `redist`
- `cache`, only for explicit cache packages
- `symbols`, only for symbol packages
- `source`, only for source packages

Symbols and source payloads are separate package classes unless an explicit package class says otherwise.

## Example File Exports

```json
{
  "file_exports": [
    {
      "target_root": "bin",
      "path": "client/dominium-client",
      "sha256": "<hash>",
      "size_bytes": 1234,
      "mode": "executable"
    },
    {
      "target_root": "packs",
      "path": "core/<pack_hash>/pack.manifest.json",
      "sha256": "<hash>",
      "size_bytes": 567,
      "mode": "read"
    }
  ]
}
```

`path` is relative to the target logical root, normalized with forward slashes, and must not contain `..`.

## Relationship To `dist/pkg`

`dist/pkg/<platform>/<arch>/` is the generated package output channel. It may contain `.dompkg` artifacts and indexes. It is not a source root and does not define install paths by itself.

## POST-CONVERGE-09 Proof Status

Package smoke proof is partial. See `docs/release/PACKAGE_SMOKE_PROOF.md`.

POST-CONVERGE-09 proved a temporary one-file `.dompkg` pack/verify smoke under `%TEMP%` and removed the output. It did not generate a release package set, package index, portable projection, or public release artifact.
