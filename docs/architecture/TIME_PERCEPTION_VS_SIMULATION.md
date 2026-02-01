Status: CANONICAL
Last Reviewed: 2026-02-01
Supersedes: none
Superseded By: none

# Time Perception vs Simulation (TIME2)





Status: draft.


Scope: separation between ACT and perceived time.





## Core Rule


ACT is authoritative and monotonic. Perception is derived and local.





## Observer Clocks


Observer clocks map ACT to perceived time with:


- dilation factor


- offset


- buffering window


- max lead/lag constraints





Observer clocks are non-authoritative and must not alter schedules.





## Use Cases


- AI autorun: accelerated perception


- Player slow-motion: dilation_factor < 1


- Spectator replay: buffered perception with fixed offset


- Multiplayer: per-client observer clocks





## References


- `schema/time/SPEC_OBSERVER_CLOCKS.md`


- `schema/time/SPEC_TIME_DILATION.md`


- `docs/architecture/SPACE_TIME_EXISTENCE.md`


- `docs/architecture/REALITY_LAYER.md`
