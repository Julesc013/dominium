Status: DERIVED
Last Reviewed: 2026-03-16
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: DOC-ARCHIVE
Replacement Target: release-pinned audit artifact retained after convergence signoff

# MVP Cross-Platform Final

## Run Summary

- result: `complete`
- gate_id: `mvp.cross_platform.gate.v1`
- deterministic_fingerprint: `d4c9816dfd00ce2b7872b7475b4e79378f978249810fe974585ca70e875b4452`
- default_degrade_event_count: `0`
- readiness: Ready for RELEASE-0.

## Per-Platform Comparison

- windows: preset=`release-win-vs2026` canonical_artifact_fingerprint=`4a31ec92c771e592849e9d2f26340908986e9f192911cfae5cf11c7fcf436b96`
- macos: preset=`release-macos-xcode` canonical_artifact_fingerprint=`4a31ec92c771e592849e9d2f26340908986e9f192911cfae5cf11c7fcf436b96`
- linux: preset=`release-linux-gcc` canonical_artifact_fingerprint=`4a31ec92c771e592849e9d2f26340908986e9f192911cfae5cf11c7fcf436b96`

## Hashes

- proof_anchor_fingerprint: `dcd804eaf04aec28ad9c40d7686d7f44f73d4d644540c974f5bddca7e36434b3`
- negotiation_record_fingerprint: `cb0411c002bd6db0e360342040a12c5581d89f20e13ac565ede3df3b0e30b570`
- pack_lock_fingerprint: `c2125f73c7de4b02aa58c64700ffbbb2f01c3e6ce38b58a4cfc23b7a8c943a8c`
- repro_bundle_fingerprint: `2ff64927ba3af69c7b416a7db8b4b71e3aa1311c2593407bd76c0627ab9c3335`
- portable_linked_parity_hash: `bf744f3cc1475e187a2f31db8c1a2d81c64174ee562009ecf2f50ec6eceb1156`
- negotiation_matrix_hash: `7113c69d64798acebc9d3298d04ae0c84da6f054c1cda85c18399b02df6e7dcf`

## Degradations

- default_lane_degrade_events: `0`
- note: canonical release comparison used host-meta-normalized hashes only; no platform-specific degrade decision entered the truth-facing artifact set.

## Mismatches

- none

## Gates

- RepoX STRICT: `PASS`
- AuditX STRICT: `PASS`
- TestX: `PASS`
- cross-platform matrix: `PASS`

## Regression Lock

- baseline_id: `mvp.cross_platform.baseline.v1`
- baseline_fingerprint: `274cee30eeb4826832536fee3865289eae8b9cb101850071e1abfeacaae456c5`
- required_commit_tag: `MVP-CROSS-PLATFORM-REGRESSION-UPDATE`
