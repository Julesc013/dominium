# Mod Extension Policy (FUTURE0)

Status: binding.
Scope: what mods may extend and what they must not change.

Mods are data extensions. They add content and contracts, not engine logic.

## Mods may add
- Data records and content packs.
- Contracts (production, refinement, travel, policy).
- Laws and capabilities (data-defined).
- Domain volumes and travel edges.
- Tools via ToolIntents (law-gated).

## Mods may not
- Modify engine or authoritative runtime code.
- Alter invariants, ACT semantics, or existence states.
- Bypass law, audit, or refusal paths.
- Fabricate entities or resources.
- Introduce nondeterministic authoritative behavior.

## Compatibility contract (mandatory)
- Mods must declare schema versions and compatibility targets.
- Refuse on mismatch; no silent fallback.
- Conflicts must be explicit and deterministic.

## Integration points
- Global schema policy: `schema/schema_policy.md`
- Mod compatibility checks: `docs/ci/CI_ENFORCEMENT_MATRIX.md`
