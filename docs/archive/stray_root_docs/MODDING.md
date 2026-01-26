# Modding Policy (FUTURE0)

Status: binding.
Scope: what mods may change and how they remain safe.

Mods are data extensions. They must preserve determinism, invariants, and law
gates. Mods do not alter engine code or authoritative execution semantics.

## Invariants
- Mods are data-only extensions.
- Law and capability gates remain mandatory.
- Determinism is mandatory for authoritative behavior.

## Mods may add
- Data content and new records.
- Contracts (production, refinement, travel).
- Institutions, organizations, and policies.
- Laws and capabilities (data-defined).
- Domains and travel edges.
- Tools via ToolIntents (law-gated).

## Forbidden assumptions
- Modify engine or authoritative runtime code.
- Alter invariants, ACT semantics, or existence states.
- Bypass law, audit, or refusal paths.
- Fabricate entities, goods, or authority.
- Introduce nondeterministic authoritative logic.

## Compatibility contract
- Schemas are versioned; mods must declare compatibility targets.
- Mismatch results in refusal, not silent fallback.
- Conflicts must be explicit and deterministically resolved.

## Dependencies
- `schema/mod_extension_policy.md`
- `schema/schema_policy.md`

## See also
- `schema/mod_extension_policy.md`
- `schema/schema_policy.md`
- `docs/guides/MODDING_GUIDE.md`
