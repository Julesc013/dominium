Status: CANONICAL
Last Reviewed: 2026-03-11
Supersedes: none
Superseded By: none

# Install Model (OPS0 / LIB-0)

Status: binding.
Scope: install identity, build identity, and store linkage.

## Authoritative Contracts

Install identity is carried by:

- `schema/install.manifest.schema` for the legacy/runtime-compatible install manifest.
- `schema/lib/install_manifest.schema` for the LIB-0 hash-pinned install descriptor.

## Rules

- Installs are immutable build roots.
- Multiple installs, versions, and forks may coexist on the same host.
- Instance manifests reference installs by `install_ref` and `install_id`; store resolution must not depend on a singleton install path.
- Shared stores may be reused across installs when hashes match; build ids remain product-local and do not affect artifact hashes.

## Linked Store Relationship

Linked instances bind an install to a store root through:

- `install_ref`
- `product_build_ids`
- `semantic_contract_registry_hash`
- `supported_protocol_versions`

This keeps binary identity separate from reusable content identity.

## Compatibility

- Existing `install.manifest.json` files remain valid.
- Legacy install roots remain explicit path entry points for launcher/setup flows.
- LIB-0 fields add hash-pinned metadata without changing authoritative build semantics.

## Related Contracts

- `docs/architecture/CONTENT_AND_STORAGE_MODEL.md`
- `docs/architecture/INSTANCE_MODEL.md`
- `schema/lib/store_root.schema`
