Status: DERIVED
Last Reviewed: 2026-03-11
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: DOC-CONVERGENCE
Replacement Target: canon-aligned documentation set for convergence and release preparation

# Repro Bundle Baseline

## Scope

DIAG-0 promotes deterministic repro capture to a first-class offline artifact.

The canonical user-facing command is `diag capture`. It writes a stable bundle
directory with:

- endpoint descriptor payloads
- session and contract context
- pack-lock and pack-compat hashes
- proof-anchor window material
- canonical event window material
- structured log window material
- optional derived view fingerprints

## Deterministic Capture Rules

- bundle file paths are stable and sorted lexicographically
- bundle hashing excludes `manifest.json` and `bundle_index.json`
- `manifest.json` stores:
  - `bundle_hash`
  - `proof_window_hash`
  - `canonical_event_hash`
  - `log_window_hash`
- replay compares the stored hashes against regenerated window hashes and
  refuses with `refusal.diag.bundle_hash_mismatch` on drift

## Privacy Boundary

- secret-like keys are stripped before bundle serialization
- account secrets, auth tokens, signing keys, and machine identifiers are not emitted
- host environment summary remains coarse host-meta only and does not influence
  replay

## Capture and Replay Workflow

1. `diag capture --out <dir> --window <ticks> [--include-views]`
2. share or archive the bundle directory offline
3. `tool_replay_bundle --bundle-path <dir> --tick-window <ticks>`
4. verify:
   - bundle hash
   - proof-window hash
   - canonical-event hash
   - log-window hash

## Integration

- AppShell command dispatch exposes `diag capture`
- supervisor crash handling reuses the DIAG-0 builder
- server console diagnostic export reuses the same builder
- IPC attach can invoke capture through the shared command surface

## Known MVP Limits

- bundle capture is directory-based rather than a single archive container
- view fingerprints are optional and remain fingerprints only
- full DIAG repro automation remains deferred until DIAG-0 successors
