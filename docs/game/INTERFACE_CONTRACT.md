Status: DERIVED
Last Reviewed: 2026-02-01
Supersedes: none
Superseded By: none

# Game Interface Contract





Status: draft (implementation gaps noted).


Scope: public game interfaces and engine boundary requirements.


Authority: canonical for required contract; blockers listed below.





## Required contract


- Game headers MUST be C++98 compatible and must not leak engine internals.


- Game APIs MUST reference schemas and capabilities, not file paths.


- No platform/render/client/server types in public game headers.


- All authoritative mutations MUST be gated by authority tokens.





## Current public surface (as-is)


- Root: `game/include/dominium/`.


- UI/render and path headers are present in the public surface (e.g., `dom_rend.h`,


  `paths.h`), violating boundary hygiene.


- Capability resolution and authority gating are not consistently documented.





## Blockers to resolve in Phase 2


- Split public vs private game headers; move UI/render/path details to private.


- Define a minimal game-facing interface that references only schemas/capabilities.


- Document ownership and error handling rules for public APIs.





## References


- `docs/architecture/CANONICAL_SYSTEM_MAP.md`


- `docs/architecture/AUTHORITY_AND_OMNIPOTENCE.md`
