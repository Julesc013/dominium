Status: CANONICAL
Last Reviewed: 2026-02-01
Supersedes: none
Superseded By: none

# Authority Model (CANON0)





Status: binding.


Scope: authority layers, capabilities, laws, and policy.





There are no game modes. There are only laws and capabilities.





## Authority layers


Authority layers are schema-defined groupings of power and responsibility.


They define which classes of actions are possible (observation, play, tooling,


governance, integrity). The exact layer set is canonical in:


`schema/authority/SPEC_AUTHORITY_LAYERS.md`.





## Capabilities vs laws vs policy


- Capabilities grant additive permission to attempt an action.


- Laws evaluate intents and return accept/refuse/transform outcomes.


- Policy constrains how actions may occur (rates, budgets, windows, scopes).





Capabilities do not bypass law; law does not imply capability.





## Profiles are data-defined configurations


These are example configurations expressed as capability sets and law policies:


- Spectator: observe-only, deny mutation and hidden info.


- Competitive: play-only, deny modified clients and external tools.


- Survival: standard play capabilities with law-enforced scarcity.


- Creative: allow mutation and free placement, deny law modification.


- Anarchy: broad capabilities, minimal policy constraints, still no existence


  or archival bypass.


- Meta-anarchy: can modify laws and grant capabilities, still fork-bound.


- Omnipotent admin: all capabilities, still law-gated and audited.





Profiles are data, not code paths.





## Law gates and audit


Every action follows intent -> law gate -> effect. Refusals are explicit and


auditable, and authority decisions always explain which capabilities and laws


were evaluated.





## See also


- `docs/architecture/AUTHORITY_AND_OMNIPOTENCE.md`


- `docs/architecture/SPECTATOR_TO_GODMODE.md`


- `docs/architecture/TOOLS_AS_CAPABILITIES.md`


- `docs/architecture/REFUSAL_AND_EXPLANATION_MODEL.md`


- `schema/authority/README.md`


- `schema/capabilities/README.md`
