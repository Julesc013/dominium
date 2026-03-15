Status: DERIVED
Last Reviewed: 2026-03-14
Stability: provisional
Future Series: DIST-7/RELEASE
Replacement Target: signed publication bundles and automated mirror promotion

# Archive And Retention Policy

## Immutable Release Principle

- Every published release must retain an immutable snapshot of:
  - `release_manifest.json`
  - `release_index.json`
  - `component_graph_hash`
  - `governance_profile_hash`
- These artifacts are immutable after publication.
- Corrections must publish a new release identity; they must not rewrite prior release records.

## Artifact Storage Model

- Release artifacts are content-addressed.
- Binary, pack, profile, lock, and bundle payloads are stored by canonical hash.
- Release manifests reference hashes and deterministic artifact names, not mutable host-specific paths.
- Archived artifact blobs are append-only; official release artifacts are never overwritten.

## Release Index History

- `release_index.json` may continue to represent the latest offline update snapshot.
- Historical release indices must be retained under:
  - `manifests/release_index_history/<channel>/<release_id>.json`
- The history path is deterministic and keyed by `release_id`, not wall-clock time.
- Rewriting an existing historical snapshot with different content is forbidden.
- Archive-history snapshots are retained beside the distributable bundle so published bundle contents do not need to be rewritten after publication.

## Mirror Strategy

- Official archival requires:
  - one primary distribution location
  - one secondary mirror
  - recommended offline cold storage
- Mirror identifiers remain provider-neutral.
- Adding or removing mirrors must update the published archive record or a superseding release publication note.

## Source Archive Policy

- For open or partially open releases, a source snapshot archive may be recorded per release.
- When present, the source archive hash must be recorded in the archive record.
- Source archive retention is additive; missing source archives do not invalidate closed-source artifact retention.

## Offline Archive Bundle

- The archive tool may produce a deterministic offline archive bundle:
  - `dominium-archive-<release_id>.tar.gz`
- The offline archive bundle is intended for cold storage and mirror seeding.
- Archive records, history snapshots, and offline archive bundles are stored beside the distributable bundle rather than injected into the live bundle payload.
- It must be assembled with:
  - deterministic file ordering
  - fixed archive metadata
  - no embedded timestamps
- The archive bundle may include:
  - all distribution artifacts
  - release indices and history snapshots
  - trust roots
  - governance profile
  - optional source archive snapshot

## Retention Guarantees

- Official mock releases have no artifact deletion policy.
- Artifacts may be added over time, but published release artifacts and history snapshots must not be removed or replaced.
- Experimental or nightly channels may define shorter retention windows later, but those rules do not apply to `v0.0.0-mock`.
