# SPEC REPLAY MODES (TIME3)

Status: draft.
Version: 1.0
Scope: canonical replay modes and interaction constraints.

## Replay Modes
LIVE_VIEW
- observer clock maps closely to ACT
- limited interaction by authority

DELAYED_VIEW
- fixed lag behind ACT
- read-only unless authority allows

ARCHIVAL_REPLAY
- fixed historical snapshot
- read-only

FORKED_REPLAY
- new timeline created (EXIST2)
- mutations allowed only in fork

## Mode Requirements
Each mode declares:
- allowed interactions
- allowed commands
- law targets
- audit requirements

## Determinism Rules
- Replay is deterministic given identical inputs.
- No ACT modification or reordering.

## Integration Points
- TIME2 observer clocks
- EXIST2 forking rules
- Law and capability gates
