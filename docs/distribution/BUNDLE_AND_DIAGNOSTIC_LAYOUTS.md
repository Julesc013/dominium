Status: PROVISIONAL
Phase: CONVERGE-04
Machine-Readable Authority: `contracts/distribution/layout.contract.toml`

# Bundle And Diagnostic Layouts

Bundles are portable exchange artifacts. They are not installs and must not be treated as install roots.

## Bundle Types

- instance bundle
- save bundle
- replay bundle
- diagnostic bundle
- compound bundle

All bundle file ordering must be deterministic. Hashes and manifests define identity, not filesystem traversal order or host paths.

## Instance Bundles

Instance bundles carry instance manifests, capability/pack locks, profile bundles, and embedded artifacts required for portable import/replay.

Instances may reference saves. They do not own authoritative save payloads unless the artifact is explicitly a compound bundle.

## Save Bundles

Save bundles carry:

- `save.manifest.json`
- snapshots
- patches
- proofs
- contract bundle references or payloads
- pack locks
- migration lineage when applicable

Save identity is hash- and manifest-pinned. Silent save migration is forbidden.

## Replay Bundles

Replay bundles carry deterministic replay inputs, event streams, version/contract references, pack locks, and verification fingerprints. They must preserve deterministic ordering and refusal evidence.

## Diagnostic Bundles

Diagnostic bundles may carry:

- logs
- events
- proofs
- hashes
- environment summaries
- command line and launch context
- contract bundle
- pack lock
- release/install/instance/save manifests

Diagnostic bundles are evidence. They do not grant authority to mutate runtime truth.

## Compound Bundles

Compound bundles may intentionally include instance and save payloads together. The manifest must state that ownership explicitly so import can preserve save truth, instance references, and embedded artifacts without guessing.
