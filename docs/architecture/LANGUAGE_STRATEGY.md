Status: CANONICAL
Last Reviewed: 2026-05-21
Supersedes: prior C89/C++98 language strategy
Superseded By: none
Stability: provisional
Future Series: LANGUAGE-BASELINE, PORTABILITY-MATRIX
Replacement Target: canon-aligned documentation set for convergence and release preparation

# Language Strategy

Status: binding.

Scope: language evolution, ABI stability, and multi-target coexistence.

## Core Rules

- C17 and C++17 are the active mainline source baselines.
- Engine C ABI spine is permanent and remains C-compatible.
- Public headers remain C17 C-compatible and C++17-consumable.
- C++17 implementation features are allowed behind registered boundaries.
- C++ ABI, STL containers, allocator objects, exceptions, and RTTI do not cross
  stable public C ABI.
- macOS 10.9.5 compatibility requires the restricted C++17 library subset in
  `contracts/build/language_baseline.contract.toml`.
- Retro C89/C++98 lanes are historical or future research only, not active
  mainline law.

## Enforcement

- Active CMake standards are C17/C++17 with extensions off.
- Public header ABI validators block C++ ABI and platform leakage.
- Language baseline validators run in fast strict.
- Capability list printed by every binary.

## See Also

- `contracts/build/language_baseline.contract.toml`
- `docs/development/LANGUAGE_BASELINE.md`
- `docs/architecture/C_COMPATIBLE_ABI_BOUNDARY.md`
