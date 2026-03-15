Status: DERIVED
Last Reviewed: 2026-03-14
Stability: provisional
Future Series: DIST-7/RELEASE
Replacement Target: published archive records and mirrored release-history automation

# ARCHIVE-POLICY-0 Retro Audit

## Current Storage Surfaces

- `release_manifest.json` is emitted under `manifests/release_manifest.json` inside assembled distribution trees.
- `release_index.json` is emitted under `manifests/release_index.json` by the offline update-model toolchain.
- Component graph identity is already carried through `release_index.json` via `component_graph_hash`.
- Governance identity is already carried through `release_index.json` via `governance_profile_hash`.

## Current Gaps Before ARCHIVE-POLICY-0

- No canonical `archive_record.json` exists yet to bind release manifest, release index, component graph, and governance profile into a single immutable retention record.
- `release_index.json` exists as a latest snapshot, but there is no governed append-only `release_index_history/` lane.
- No deterministic offline archive bundle exists for cold-storage export.
- Source archive retention is policy-described in governance, but not yet recorded per release artifact set.

## Artifact Blob Storage

- Distribution and pack payloads are already content-addressed by hash through the store and release-manifest layers.
- Release manifests reference artifact hashes rather than mutable blob names.
- Shared-store and dist assembly tooling already operate on deterministic artifact identities.

## Source Archive Preservation

- No per-release source snapshot archive is automatically emitted today.
- Source archive capture is therefore optional and must remain additive for open or partially open governance modes.

## Summary

- Existing release surfaces already expose the hashes needed for long-term archival.
- The missing layer is retention policy: immutable archive records, append-only release-index history, deterministic offline archive bundles, and mirror declarations.
