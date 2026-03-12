Status: RELEASE-LOCKED
Last Reviewed: 2026-03-13
Scope: v0.0.0 frozen invariant declaration.

# Frozen Invariants v0.0.0

The following invariants are frozen for `v0.0.0`.
They may not change without a semantic contract bump, a migration plan when persisted data is involved, and the explicit regression-update tag required by the affected lock.

## Semantic Contract Registry v1

Frozen registry-backed semantic contracts:

- `contract.geo.metric.v1`
- `contract.overlay.merge.v1`
- `contract.logic.eval.v1`
- `contract.worldgen.refinement.v1`
- `contract.cap_neg.negotiation.v1`
- `contract.pack.compat.v1`
- `contract.time.anchor.v1`
- `contract.appshell.lifecycle.v1`

Registry hash frozen at scope lock:

- `semantic_contract_registry_hash`: `500f86d45022f5fffb44b7e425bacb2e0b9b98601064c9416f9bb923fdac1334`

Requested but not declared in the current semantic contract registry:

- `contract.lib.manifest.v1`
  - This contract is not introduced by `SCOPE-FREEZE-0`.
  - Adding it here would create a new semantic surface, which is out of scope for convergence lock work.

## Determinism Guarantees

- Truth paths use fixed-point or approved deterministic integer math only.
- Authoritative randomness uses named RNG streams only.
- Simulation time does not derive from wall-clock time.
- Canonical artifacts use deterministic serialization everywhere hashes are derived.

## Content Addressing Guarantees

- Packs, profiles, blueprints, saves, locks, manifests, repro bundles, and proof artifacts are content-addressed by canonical hash.
- Path-based identity is not authoritative.

## UI Mode Selection Order

Automatic UI mode selection is frozen as:

1. explicit override
2. OS-native
3. rendered
4. TUI
5. CLI

This freeze governs future convergence work.
It does not authorize a semantic behavior change where current products still default directly to CLI or headless when no automatic selection path is active.

## Epoch Anchor Model

- `tick_t` is frozen as a 64-bit canonical tick type.
- Epoch anchors remain aligned to the deterministic anchor interval from `time_anchor_policy_registry`.
- Compaction boundaries remain anchored to epoch anchors.

## Change Control

These invariants may not change without:

- semantic contract bump
- migration plan
- regression update tag
