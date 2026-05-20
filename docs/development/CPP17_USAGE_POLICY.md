Status: DERIVED
Last Reviewed: 2026-05-21
Supersedes: `docs/development/cpp98_implementation_standard.md` as active mainline policy
Superseded By: none
Stability: provisional
Binding Sources: `contracts/build/language_baseline.contract.toml`, `contracts/abi/language_boundary.contract.toml`

# C++17 Usage Policy

C++17 is the active C++ language floor for Dominium mainline implementation.

Use C++17 for code that benefits from ownership, resource lifetime control,
typed composition, backend abstraction, and tool complexity:

- game/domain orchestration
- runtime services
- renderer and platform backends
- client/server/launcher/setup/workbench apps
- job systems
- diagnostics
- compiled tooling

## Boundary Rules

- Do not expose C++ classes, templates, STL containers, exceptions, RTTI, or
  overloaded C++ ABI as stable public C ABI.
- Do not let exceptions cross public ABI boundaries.
- Keep stable module/provider/product boundaries registered as public surfaces.
- Use C-compatible wrappers for cross-toolchain, provider, module, or long-lived
  binary surfaces.

## Allowed Internally

- RAII and move-only ownership
- `std::unique_ptr`
- `std::atomic` where deterministic law and thread-count invariance are not
  compromised
- `std::optional` and `std::variant` only under the macOS 10.9.5 subset rules
- STL containers in private implementation where allocator/lifetime does not
  cross public ABI

## Determinism

C++17 improves implementation structure; it does not relax deterministic law.
Authoritative scheduling must not depend on wall clock, thread completion
order, pointer order, unspecified hash iteration order, or platform object
layout.
