Status: DERIVED
Last Reviewed: 2026-03-27
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: XI-5
Replacement Target: XI-5 bounded execution against approved mapping lock

# XI-4Z Approved Layout

## Selected Layout

- Selected option: `C`
- Approved-for-XI-5 rows: `770`
- Approved-to-attic rows: `23`
- Deferred-to-XI-5b rows: `2`

## Domain Set

- `engine`
- `game`
- `apps`
- `tools`
- `lib`
- `compat`
- `ui`
- `platform`
- `tests`
- `attic`

## Rationale

- Option C remains the default because XI-4b already marked it preferred and no stronger contradictory evidence is present.
- It preserves the lowest recorded Xi-5 complexity while keeping the highest automatic move count.
- Its lower immediate normalization pressure matches the bounded XI-5a requirement.
- Explicit attic approvals are exceptions to the active layout baseline, not evidence against Option C.
- Current metrics: automatic=`663` manual=`132` attic=`0` complexity=`LOW`.

## What Remains Provisional

- the approved lock is provisional and exists only to constrain XI-5 execution
- deferred rows remain outside the XI-5a move batch and must be reconsidered in XI-5b or later
- final repository freeze still waits for XI-5 through XI-8
