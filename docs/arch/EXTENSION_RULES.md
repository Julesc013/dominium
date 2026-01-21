# Extension Rules (FUTURE0)

Status: binding.
Scope: how new systems and features are added without violating canon.

All new systems must be introduced as extensions, not replacements. The
canonical model is not redefined by implementation convenience.

## Required properties of any new system
- Express intent -> law/capability gate -> effect -> audit.
- Emit Work IR for authoritative work.
- Declare invariants preserved and invariants consumed.
- Define refusal and absence behavior.
- Bind all spatial behavior to domains and travel.
- Bind all time to ACT scheduling and observer clocks.

## Required documentation updates
When adding a system, you must update:
- `docs/arch/CANONICAL_SYSTEM_MAP.md` (new family + dependencies).
- `docs/arch/INVARIANTS.md` (invariants preserved/enforced).
- Schema indexes under `schema/` if new data formats are added.
- `docs/ci/CI_ENFORCEMENT_MATRIX.md` with new enforcement IDs.

## Data-first extension
Prefer data and contracts over code for gameplay variation:
- New laws and capabilities are data-defined.
- New production chains, institutions, and policies are schema-defined.
- New content lives under `data/` and must be validated.

## Forbidden extension patterns
- Backdoor code paths that bypass law or audit.
- Implicit existence or resource creation for convenience.
- Unbounded global iteration or per-tick loops.

## See also
- `docs/arch/FUTURE_PROOFING.md`
- `schema/schema_policy.md`
- `schema/mod_extension_policy.md`
