Status: DERIVED
Last Reviewed: 2026-03-14
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: STORE-GC
Replacement Target: release-pinned store lifecycle bundles and transaction-backed shared-store cleanup

# Store Integrity and GC

## Store Integrity Checks

- Verify `store.root.json` exists.
- Verify every artifact directory name is a canonical content hash.
- Verify `artifact.manifest.json` exists for every stored artifact.
- Verify manifest category and hash match the directory layout.
- Verify payload bytes or tree entries reproduce the canonical content hash.
- Detect partial writes by refusing missing manifest or missing payload cases.

## Reference Graph

Artifacts are reachable only when referenced by governed manifests:

- install manifests
- instance manifests
- save manifests
- release manifests and release-index caches
- pinned bundle manifests

Nested references must also be followed deterministically:

- pack lock -> pack hashes

## GC Policies

- `gc.none`
  - default for mock
  - report only
  - no store mutation
- `gc.safe`
  - delete only unreachable artifacts indirectly by moving them into quarantine
  - quarantine path is deterministic: `store/quarantine/<category>/<hash>`
- `gc.aggressive`
  - deletes only unreachable artifacts
  - requires an explicit destructive flag

## Determinism

- Reachability traversal is deterministic and sorted.
- Nested traversal order is deterministic and sorted.
- Candidate deletion order is deterministic and sorted.
- GC reports are canonical serialized and content-hashed.
- No wall-clock time is used for verification, traversal, quarantine naming, or deletion order.

## Portable Bundles

- Portable bundles are self-contained and protected from GC by default.
- GC must refuse portable stores unless the caller explicitly supplies an override.
- Shared installed-mode stores may be cleaned only after verification and reachability planning succeed.
