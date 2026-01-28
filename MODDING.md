# Modding Policy (FUTURE0)

Status: binding.
Scope: modding boundaries, compatibility, and invariant protection.

Mods are data extensions. They must preserve determinism, invariants, and
law gates. Mods do not alter engine code or authoritative execution semantics.

## Invariants
- Mods add data and contracts; they do not change runtime logic.
- Law and capability gates remain mandatory.
- No fabrication of entities, goods, or authority.

## Mods may add
- Data content and new records.
- Contracts (production, refinement, travel).
- Institutions, organizations, and policies.
- Laws and capabilities (data-defined).
- Domains and travel edges.
- Tools via ToolIntents (law-gated).

## Forbidden assumptions
- Mods can modify engine or authoritative runtime code.
- Mods can alter invariants, ACT semantics, or existence states.
- Mods can bypass audit or law gates.
- Mods can introduce nondeterministic authoritative behavior.

## Compatibility contract
- Schemas are versioned; mods must declare compatibility targets.
- Mismatch results in refusal, not silent fallback.
- Conflicts must be explicit and deterministically resolved.

## Dependencies
- `schema/mod_extension_policy.md`
- `schema/schema_policy.md`
- `docs/ci/CI_ENFORCEMENT_MATRIX.md`

## See also
- `docs/architecture/EXTENSION_RULES.md`
- `docs/MODDING.md`
