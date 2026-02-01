Status: CANONICAL
Last Reviewed: 2026-02-01
Supersedes: none
Superseded By: none

# Floating Point Policy (DETER-0)

Status: binding.
Scope: floating point usage across the codebase.

## Core rule
Authoritative simulation logic MUST NOT use floating point (`float`, `double`,
`long double`) or math intrinsics. Fixed-point is required for deterministic
simulation behavior.

## Allowed FP zones (presentation only)
Floating point is permitted ONLY in:
- client rendering
- UI layout and presentation
- visualization tools and offline analysis

FP usage MUST NOT affect authoritative state or outcomes.

## Enforcement
Static analysis and TestX checks enforce:
- no FP types in authoritative paths
- no math intrinsics in authoritative paths

## See also
- `docs/architecture/UNIT_SYSTEM_POLICY.md`
- `docs/architecture/DETERMINISTIC_ORDERING_POLICY.md`