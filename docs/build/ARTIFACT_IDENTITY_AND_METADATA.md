Status: DERIVED
Last Reviewed: 2026-02-01
Supersedes: none
Superseded By: none

# Artifact Identity and Metadata

## Canonical Naming

Artifacts keep the canonical filename scheme:

```
<product>-<semver>+build.<n>-<os>-<arch>-<renderer>-<config>
```

Notes:

- `<renderer>` may be `multi` for binaries that embed multiple backends.
- The naming scheme is unchanged by SKUs.

## Sidecar Metadata

Use the artifact metadata generator:

```
dom_tool_artifactmeta --input <path> --output <path>.json --format json
```

The sidecar JSON includes:

- Product identity (name, semver, build id/number, SKU).
- Target identity (`os`, `arch`, `renderer`, `config`, `artifact_name`).
- Toolchain descriptor fields.
- Protocol/API/ABI versions.
- SHA-256 hashes for the artifact and sidecar.
- `dependencies.packs_required` (must allow none).

### Sidecar Hash Basis

`hashes.sidecar_sha256` is computed over the JSON content with
`sidecar_sha256` set to an empty string. The basis is recorded as:

```
hashes.sidecar_hash_basis = "json_without_sidecar_sha256"
```

This avoids recursive self-hashing.

## Example

```json
{
  "schema_version": 1,
  "artifact": { "path": "bin/client.exe", "file_name": "client.exe", "size": 1234, "sha256": "..." },
  "identity": { "product": "client", "product_version": "0.0.0", "artifact_name": "client-0.0.0+build.42-winnt-x64-multi-Debug" }
}
```