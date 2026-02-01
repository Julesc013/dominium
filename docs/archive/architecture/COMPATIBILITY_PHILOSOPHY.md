Status: HISTORICAL
Last Reviewed: 2026-02-01
Supersedes: none
Superseded By: docs/architecture/CANON_INDEX.md

This document is archived.
Reason: Superseded by docs/architecture/CANON_INDEX.md.
Do not use for implementation.

This document is archived.
Reason: Superseded by docs/architecture/CANON_INDEX.md.
Do not use for implementation.

This document is archived.
Reason: Superseded by unknown.
Do not use for implementation.

# ARCHIVED — OUTDATED





This document is archived and superseded by `docs/architecture/FUTURE_COMPATIBILITY_AND_ARCH.md`.


Reason: EG-H canon designates `docs/architecture/` as authoritative; this file may


conflict or duplicate canonical compatibility rules.


Status: archived for historical reference only.





# Compatibility Philosophy





Status: canonical.


Scope: compatibility for engine, game, saves, replays, packs, and mods.


Authority: canonical. All other docs MUST defer to this file for compatibility.


Any change to this contract SHALL be treated as an explicit breaking revision.





## Binding contract


- Compatibility MUST be determined by declared capabilities and schema


  compatibility. Version numbers alone MUST NOT be treated as sufficient.


- Saves MUST be structural facts, not behavior. They MUST record objective


  state, provenance, and authority scope, and MUST NOT encode execution logic.


- Schemas MUST be forward-compatible. Unknown fields and tags MUST be preserved


  unless explicitly rejected by policy.


- Replays MUST be treated as archival truth. They MUST reproduce authoritative


  outcomes when compatible and MUST refuse when not.


- Loud failure MUST override silent coercion. Incompatible artifacts MUST


  refuse or enter an explicit compatibility mode.





## Compatibility modes (explicit)





### Authoritative


Definition: Full compatibility for authoritative simulation.


Rules: Required capabilities and schemas MUST match declared constraints. The


simulation MUST produce authoritative outcomes.





### Degraded simulation


Definition: Authoritative simulation with non-authoritative capabilities


disabled or reduced.


Rules: Degradation MUST be explicit and logged. Authoritative outcomes MUST NOT


change as a result of degradation.





### Frozen (inspection or replay only)


Definition: Read-only access to objective state or replay verification.


Rules: Authoritative mutation MUST NOT be permitted. Only inspection or replay


verification is allowed.





### Transform-only


Definition: Compatibility through deterministic migration or conversion only.


Rules: Only transforms SHALL run. Live simulation MUST NOT run in this mode.





## Guarantees


- No silent breakage for saves, replays, mods, or packs.


- Deterministic resolution for the same inputs and artifacts.


- Unknown field preservation when forward compatibility is declared.


- Explicit refusal with reasons when compatibility cannot be guaranteed.





## Not guaranteed


- Semantic identity across engine versions.


- Compatibility for artifacts that violate declared capability or schema bounds.


- Stability of derived or presentation-only data.





## Reasoning for users and tools


Users and tools SHALL treat compatibility as capability negotiation plus schema


validation. If requirements are unmet, only Frozen or Transform-only modes are


allowed.





## References


- `docs/architectureitecture/INVARIANTS.md`


- `docs/architectureitecture/TERMINOLOGY.md`


- `docs/schema/FORWARD_COMPATIBILITY.md`


- `docs/pack_format/PACK_MANIFEST.md`


- `docs/content/UPS_OVERVIEW.md`
