# Packaging Matrix

Status: PROVISIONAL

Phase: CONVERGE-11

Machine-readable source: `contracts/release/component_matrix.contract.toml`

Related projection authority:

- `contracts/distribution/layout.contract.toml`
- `docs/repo/DISTRIBUTION_LAYOUT_CANON.md`

## POST-CONVERGE-09 Evidence Note

Package/projection smoke proof is partial. See `docs/release/PACKAGE_SMOKE_PROOF.md` and `docs/distribution/PORTABLE_PROJECTION_SMOKE_PROOF.md`.

| Lane | POST-CONVERGE-09 Status | Evidence | Blocker |
| --- | --- | --- | --- |
| dompkg | partial | temporary one-file smoke package packed and verified | not a release package set |
| portable_install | blocked | contract and expected layout validated by dry-run audit | no build output, binaries, or generated manifests |
| portable_zip | blocked | packaging pipeline `portable` help exists | no assembled artifact root |
| dist_output | partial | package/dist tooling and CMake targets exist | no built products or generated package tree |

No package row is promoted to `available` or `implemented` by this proof.

## Package Rows

| Package Lane | Status | Tier | Notes |
| --- | --- | --- | --- |
| dompkg | provisional | T0 | Package exports use logical roots, not absolute host paths. |
| portable_zip | planned | T0 | Archive extraction must produce a valid portable install. |
| tarball | planned | T0 | Deterministic archive lane. |
| app_bundle | planned | T1 | macOS app bundle lane. |
| installer | planned | T2 | Windows/Linux/macOS installer lane. |
| server_bundle | planned | T0 | Server install/runtime projection lane. |
| tools_bundle | planned | T2 | Shipped tools bundle lane after tool classification. |
| media_offline_bundle | planned | T2 | Offline/burn-to-media projection. |
| symbols_debug_package | planned | T1 | Separate symbols/debug channel. |
| source_archive | planned | T2 | Optional source archive projection. |

## Distribution Projections

| Projection | Status | Tier | Notes |
| --- | --- | --- | --- |
| source_repo | available | T0 | Governed by source layout contracts. |
| dist_output | provisional | T0 | Generated output, not source authority. |
| compressed_archive | planned | T0 | Extracts to portable install. |
| portable_install | planned | T0 | Self-describing install/store layout. |
| installed_desktop | planned | T1 | Immutable install plus mutable user/store roots. |
| server_install | planned | T0 | Server/system projection. |
| media_layout | planned | T2 | Read-only media payload by default. |
| package_export | provisional | T0 | `.dompkg` logical root export model. |
| bundle_export | provisional | T0 | Instance/save/replay/diagnostic bundle model. |
| cache_and_staging | provisional | T0 | Cache, staging, and transaction projection. |
| symbols_and_provenance | planned | T1 | Separate symbols/provenance channel. |

## Rule

Packages export into logical roots. They must not encode absolute host install paths.
