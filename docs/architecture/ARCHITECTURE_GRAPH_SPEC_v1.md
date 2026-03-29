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
- graph content hash: `a63f8a3ec1a091b9bd0737f69a652ee0232e0b734f13bfbec0e5fcf36b68bb39`
- graph fingerprint: `ff1c955301dd733e8269f2ec3c5052de98c705a6a1d487990fb6d6e45e2da5ea`
- module registry id: `module_registry.v1`
- module registry content hash: `7ace1eeef021f575527bf96f6fc604dbabef025e734db2c0ade5b681269c9d05`
- module count: `1735`
- concept count: `319`
- canonical semantic engines: `9`

## Freeze Rules

- `architecture_graph.v1.json` is the authoritative structural baseline for Xi-6 and later drift checks.
- live architecture changes require an `ARCH-GRAPH-UPDATE` tag before the frozen baseline may diverge.
- module roots must remain registered; new unregistered module roots are invariant failures.
- frozen graph hashes are computed canonically and must not depend on wallclock state.

## Provisional Notes

- `unknown.root` is retained as a provisional repo-support surface pending later non-runtime cleanup.
- transitional compat helpers still located under `tools.compatx.core` and `tools.xstack.compatx` are treated as explicit support bridges during Xi-6.
