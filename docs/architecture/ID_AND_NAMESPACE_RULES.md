Status: CANONICAL
Last Reviewed: 2026-02-01
Supersedes: none
Superseded By: none

# ID And Namespace Rules (IDNS0)





Status: binding.


Scope: identifier shape, stability, and reserved namespaces across the repo.





This document tightens and extends:


- `docs/architecture/NAMESPACING_RULES.md`


- `docs/architecture/GLOBAL_ID_MODEL.md`


- `docs/architecture/SEMANTIC_STABILITY_POLICY.md`





## Canonical identifier rules


- All identifiers MUST be reverse-DNS style tokens.


- Identifiers MUST be ASCII and case-insensitive.


- The canonical stored form is lowercase ASCII.


- Identifiers MUST be opaque. Code MUST NOT infer meaning from substrings.


- Identifiers MUST be stable across versions.


- Identifiers MUST NEVER be reused with a new meaning.


- If meaning must change incompatibly, mint a new identifier.


- Legacy symbolic refusal tokens (for example `REFUSE_*`) are reserved


  exceptions; their numeric `code_id` remains the canonical identifier.





Reverse-DNS here means a dot-separated namespace owned by a provider, followed


by a stable local name, for example: `dominium.schema.process`.





Reserved reverse-DNS aliases for refusal families live under:


- `dominium.refusal.*`





## ID classes covered by this policy


This policy is binding for the following identifier families:


- capability IDs


- process_family IDs


- field IDs


- material IDs


- part IDs


- assembly IDs


- standard IDs


- refusal codes (symbolic tokens; numeric codes are separate and stable)


- save chunk IDs


- schema IDs





## Reserved namespaces and ranges


These reservations are stability surfaces. They are intentionally conservative.





Reserved for core engine and canonical architecture:


- `domino.*`


- `dominium.*`


- `org.domino.*`


- `org.dominium.*`





Reserved for canonical game-owned IDs (still content-agnostic in code):


- `dominium.game.*`


- `org.dominium.game.*`





Reserved for tools and operational surfaces:


- `dominium.tools.*`


- `org.dominium.tools.*`





Reserved for mods and external providers:


- `org.<provider>.*` where `<provider>` is not `dominium` or `domino`


- `mod.local.*` for local development and experiments only





Reserved for future extensions and staging:


- `dominium.ext.*`


- `org.dominium.ext.*`


- `dominium.future.*`





## Stability and reuse contract


- A released identifier is permanent.


- Reuse is treated as a schema and ABI break.


- Collisions within an ID class are refusals.


- Unknown identifiers MUST be preserved or refused, never guessed.





## Implementation guidance (non-normative)


- Compare identifiers by lowercase ASCII bytes.


- Validate identifiers at load time, not in hot paths.


- Prefer registry resolution from IDs to data-owned meaning.





## See also


- `docs/architecture/REGISTRY_PATTERN.md`


- `docs/architecture/REFUSAL_SEMANTICS.md`


- `docs/architecture/CONTRACTS_INDEX.md`
