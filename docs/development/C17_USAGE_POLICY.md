Status: DERIVED
Last Reviewed: 2026-05-21
Supersedes: `docs/development/c89_coding_standard.md` as active mainline policy
Superseded By: none
Stability: provisional
Binding Sources: `contracts/build/language_baseline.contract.toml`, `contracts/abi/c_api.contract.toml`

# C17 Usage Policy

C17 is the active C language floor for Dominium mainline.

Use C17 for code that should remain plain, auditable, deterministic,
C-callable, or ABI-adjacent:

- public C-compatible headers
- fixed-point math
- deterministic RNG streams
- stable IDs and handles
- canonical hashing
- packets and command structs
- save/replay encoders
- renderer command IR
- platform/provider C facades

## Rules

- Keep stable public ABI C-compatible and POD-oriented.
- Use opaque handles for owned objects crossing ABI boundaries.
- Include `struct_size` on ABI-visible config/options/descriptor/vtable structs.
- Include `api_version` when forward/backward compatibility is required.
- Use explicit allocator or destroy/free APIs when allocation crosses a boundary.
- Return explicit result or refusal codes.
- Do not serialize raw C struct layout as save, replay, network, or package
  format.
- Do not use hidden mutable globals for public API state.

## Cross-Platform Caveat

Do not rely on C17 atomics, threads, or complex-number support as the portable
cross-platform concurrency substrate. Use the project abstraction or C++17
`std::atomic` behind implementation boundaries where appropriate.

## Public Header Compatibility

Public C headers may use C17 syntax where it does not leak platform or C++ ABI
requirements. They still must be consumable from C++ through `extern "C"` when
they expose C functions.
