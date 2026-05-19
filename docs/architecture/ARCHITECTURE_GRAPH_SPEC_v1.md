Status: DERIVED
Last Reviewed: 2026-03-30
Stability: stable
Future Series: XI-6
Replacement Target: superseded by a later explicit ARCH-GRAPH-UPDATE freeze only

# Architecture Graph Spec v1

This document freezes the post-Xi-5 architecture graph as the canonical Xi-6 baseline.

## Identity

- graph id: `architecture_graph.v1`
- graph contract id: `contract.arch.graph.v1`
- graph content hash: `f3c7b9cde7f94c3419497cdc922c46e6cd4b09837ba224a1106d55627d16bdb6`
- graph fingerprint: `f382a8cbb8f8d786d1c73fca7bd59de94391195b5c00e5b0b65dc3762343777b`
- module registry id: `module_registry.v1`
- module registry content hash: `2d1fac982f3aae4339b1ce0b9bb9a74db358d84a07b5ed9c661eada0a1304783`
- module count: `2210`
- concept count: `177`
- canonical semantic engines: `9`

## Freeze Rules

- `architecture_graph.v1.json` is the authoritative structural baseline for Xi-6 and later drift checks.
- live architecture changes require an `ARCH-GRAPH-UPDATE` tag before the frozen baseline may diverge.
- module roots must remain registered; new unregistered module roots are invariant failures.
- frozen graph hashes are computed canonically and must not depend on wallclock state.

## Provisional Notes

- `unknown.root` is retained as a provisional repo-support surface pending later non-runtime cleanup.
- transitional compat helpers still located under `tools.xstack.compatx.core` and `tools.xstack.compatx` are treated as explicit support bridges during Xi-6.
