# Spectator and Audit Modes (TIME3)

Status: draft.
Scope: spectator views, buffered inspection, and audit replay.

## Spectator Modes
- LIVE_VIEW: near-ACT, read-only unless authority permits
- DELAYED_VIEW: fixed lag behind ACT
- ARCHIVAL_REPLAY: historical snapshot
- FORKED_REPLAY: new timeline for analysis

## Audit and Dispute Use
- Deterministic step-through
- Explanation graphs
- Read-only by default

## Constraints
- No future leakage beyond permissions
- No ACT modification
- All access is law- and capability-gated

## References
- `schema/time/SPEC_REPLAY_MODES.md`
- `schema/time/SPEC_BUFFERED_PERCEPTION.md`
- `docs/arch/AUTHORITY_IN_REALITY.md`
