Status: CANONICAL
Last Reviewed: 2026-03-11
Supersedes: none
Superseded By: none

# Install Model (OPS0 / LIB-1)

Status: binding.
Scope: install identity, product build selection, store linkage, and multi-install coexistence.

## Authoritative Contracts

Install identity is carried by:

- `schema/install.manifest.schema` for the legacy/runtime-compatible install manifest.
- `schema/lib/install_manifest.schema` for the LIB-1 hash-pinned install descriptor.
- `schema/lib/product_build_descriptor.schema` for per-product binary + endpoint descriptor identity.

## Rules

- Installs are immutable build roots with explicit product-build membership.
- Multiple installs, versions, and forks may coexist on the same host.
- Instance manifests reference installs by `install_ref`, `install_id`, and optional `required_product_builds`; store resolution must not depend on a singleton install path.
- Shared stores may be reused across installs when hashes match; build ids remain product-local and do not affect artifact hashes.
- Install validation must refuse missing binaries, binary hash mismatches, descriptor hash mismatches, and semantic contract registry mismatches.

## Linked Store Relationship

Linked installs and linked instances bind to a store root through:

- `store_root_ref`
- `product_builds`
- `semantic_contract_registry_hash`
- `supported_protocol_versions`
- `supported_contract_ranges`

This keeps binary identity separate from reusable content identity while preserving deterministic build selection.

## Portable Install Layout

Portable installs must be self-describing at the install root:

- `install.manifest.json`
- `semantic_contract_registry.json`
- `bin/`
- `store/`
- `instances/`
- `saves/`

Descriptor sidecars may live adjacent to binaries under `bin/`.

## Registry Coexistence

- Host registration is tracked in `data/registries/install_registry.json`.
- Registry order is deterministic by `install_id`.
- Registry membership is operational metadata only and does not change install identity.

## Build Selection

- Launcher preflight must verify `required_product_builds` against the selected install.
- Launcher preflight must verify `required_contract_ranges` against the selected install.
- On mismatch, inspect/replay flows may degrade to inspect-only; otherwise the launcher must refuse with remediation.

## Compatibility

- Existing `install.manifest.json` files remain valid.
- Legacy install roots remain explicit path entry points for launcher/setup flows.
- LIB-1 fields add hash-pinned metadata, per-product build identity, and install registry linkage without changing authoritative simulation semantics.

## Related Contracts

- `docs/architecture/CONTENT_AND_STORAGE_MODEL.md`
- `docs/architecture/INSTANCE_MODEL.md`
- `docs/audit/INSTALL_MANIFEST_BASELINE.md`
- `schema/lib/store_root.schema`
