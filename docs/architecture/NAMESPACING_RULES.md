Status: CANONICAL
Last Reviewed: 2026-02-01
Supersedes: none
Superseded By: none

# Namespacing Rules (NS0)





Status: binding.


Scope: namespace requirements for identifiers.





## Required namespaces


Identifiers MUST be namespaced (reverse-DNS or equivalent provider-owned hierarchical tokens) for:


- capabilities


- fields


- processes


- chunk types


- policies


- metrics


- units


- packs and modpacks





## Rules


- No reuse of identifiers with new meaning.


- Collisions are refusals.


- Reserved namespaces are owned by their providers.
- Pack ids use `official.<org>.<pack>`, `mod.<author>.<pack>`, `fork.<origin_pack_id>.<fork_author>.<fork_name>`, or `local.<user>.<pack>`; legacy reverse-DNS pack ids remain compatibility-only.





## See also


- `docs/architecture/SEMANTIC_STABILITY_POLICY.md`


- `docs/architecture/UNIT_SYSTEM_POLICY.md`
