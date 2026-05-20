Status: DERIVED
Last Reviewed: 2026-05-20
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: API-ABI-CANON, DEPENDENCY-DIRECTION, PROVIDER-MODEL
Binding Sources: `contracts/abi/c_api.contract.toml`, `contracts/abi/language_boundary.contract.toml`

# C++98 Implementation Standard

## Scope

C++98 may be used internally where the owning component and toolchain support it.
This does not make C++ a stable public ABI surface.

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
