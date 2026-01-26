# Namespacing Rules (NS0)

Status: binding.
Scope: namespace requirements for identifiers.

## Required namespaces
Identifiers MUST be namespaced (reverse-DNS or equivalent) for:
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

## See also
- `docs/arch/SEMANTIC_STABILITY_POLICY.md`
- `docs/arch/UNIT_SYSTEM_POLICY.md`
