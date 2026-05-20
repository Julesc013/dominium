Status: DERIVED
Last Reviewed: 2026-05-21
Supersedes: none
Superseded By: `docs/development/CPP17_USAGE_POLICY.md`
Stability: provisional
Future Series: API-ABI-CANON, DEPENDENCY-DIRECTION, PROVIDER-MODEL
Binding Sources: `contracts/abi/c_api.contract.toml`, `contracts/abi/language_boundary.contract.toml`

# Historical C++98 Implementation Standard

This file is retained as historical rationale. It is no longer the active
mainline language floor. The active C++ policy is
`docs/development/CPP17_USAGE_POLICY.md`, and the build-enforced baseline is
`contracts/build/language_baseline.contract.toml`.

## Scope

C++98 was previously used internally where the owning component and toolchain
supported it. C++17 now governs mainline implementation. This still does not
make C++ a stable public ABI surface.

## Boundary Rules

- Do not expose C++ classes, templates, STL containers, exceptions, or overload
  semantics through stable public C ABI.
- Keep C++ implementation behind C-compatible wrappers when a surface is public
  across tools, providers, modules, or products.
- Do not allow exceptions to cross ABI boundaries.
- Use STL only in internal implementation or explicitly C++-scoped internal
  headers.
- Avoid compiler-specific extensions in portable implementation code unless the
  surface documents the toolchain scope.
- Preserve public ABI stability through registered contracts, not by treating a
  class layout as stable.

## Replacement Freedom

Internal C++ classes, containers, and algorithms may be replaced without
compatibility promises unless a public surface registry entry explicitly
promotes them.
