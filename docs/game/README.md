Status: DERIVED
Last Reviewed: 2026-02-01
Supersedes: none
Superseded By: none

# Game Layer Documentation





This directory defines the authoritative game-layer contracts. Canonical


architecture rules live in `docs/architectureitecture/INVARIANTS.md` and


`docs/architectureitecture/TERMINOLOGY.md`. If there is any conflict, those documents


are authoritative.





## Scope





- The game layer MUST implement rules using engine primitives only.


- The game layer MUST remain content-agnostic and MUST boot with zero assets.


- The game layer MUST be deterministic and replay-safe.


- The game layer MUST NOT include platform, renderer, audio, or OS code in


  authoritative logic.





## Canonical Game Interfaces





The game layer exposes primitive interfaces that bind rules to engine


primitives:





- Work IR emission: `game/include/dominium/execution/system_iface.h`


- Process descriptor providers: `game/include/dominium/execution/process_iface.h`


- Epistemic (subjective) capability views: `game/include/dominium/epistemic.h`


- UPS pack registration helpers: `game/include/dominium/ups_runtime.h`





## Enforcement Status (Explicit)





To preserve current behavior, the following requirements are specified but not


yet enforced in game code:





- All rule mutations flowing through the process interface.


- Authority token enforcement on every mutating rule path.


- Compatibility negotiation applied to pack/mod/save resolution.


- UPS registry integration into instance selection and pack graphs.





These gaps are deliberate and require an explicit breaking revision.





## Non-Features (Game Layer)





- The game layer MUST NOT embed content, assets, or default worlds.


- The game layer MUST NOT assume any specific platform, renderer, or client.


- The game layer MUST NOT silently coerce incompatible packs or saves.
