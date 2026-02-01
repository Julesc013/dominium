Status: CANONICAL
Last Reviewed: 2026-02-01
Supersedes: none
Superseded By: none

# COMPATIBILITY_PROMISES (FINAL0)





Status: draft


Version: 1





Canonical policy summary: `docs/architectureitecture/COMPATIBILITY_PHILOSOPHY.md`.





## Purpose


Define the compatibility promises for saves, replays, and mods.





## Saves


- Saves must never silently break.


- Unsupported schema major versions must refuse or migrate deterministically.


- Save metadata must include schema versions and feature epochs.


- Save metadata must include authority scope.





## Replays


- Replays must be replayable under pinned versions.


- If required schemas or epochs are missing, replays must refuse.





## Mods


- Mods must refuse or degrade deterministically (see MOD0).


- Sim-affecting incompatible mods must refuse; no silent disable.


- Non-sim mods may be disabled only via explicit safe mode.





## Schema major changes


- Any schema major bump requires a migration or explicit refusal path.


- Changes must be recorded in compatibility notes.





## Packs (UPS)


- Pack resolution is deterministic and independent of filesystem order.


- Unknown pack tags must be preserved for forward compatibility.


- Pack capability changes that affect simulation require refusal or migration.





## Explicit degradation (non-sim only)


- Non-sim capabilities may be disabled (UI, rendering, tooling).


- Representation tiers may degrade explicitly (explicit -> hybrid -> procedural).


- Null or headless backends are valid when presentation is unavailable.


- Authoritative outcomes must not change as a result of degradation.





## Prohibitions


- Silent breaking changes.


- Implicit fallback that alters simulation outcomes.
