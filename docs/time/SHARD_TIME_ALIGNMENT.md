Status: DERIVED
Last Reviewed: 2026-03-16
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: DOC-CONVERGENCE
Replacement Target: canon-aligned documentation set for convergence and release preparation

# Shard Time Alignment

Date: 2026-03-04  
Scope: TEMP-2

## Rules

- Canonical tick alignment across shards is mandatory.
- Shards do not mutate canonical tick independently.
- Drift applies only to derived domain time (civil/proper/warp), never canonical tick.
- Cross-shard synchronization must use explicit boundary/signal artifacts.
- No implicit global synchronization service is allowed.

## Causality

- Sync correction consumes received artifacts only.
- Future receipts are invalid under existing causality invariants.
- Rejections/corrections must be logged deterministically.

## Replay

- Replay windows must reproduce:
  - domain mapping hash chains
  - schedule-domain evaluation hash
  - time-adjust event hash chain
