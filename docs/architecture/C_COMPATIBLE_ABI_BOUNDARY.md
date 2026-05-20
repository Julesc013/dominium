Status: DERIVED
Last Reviewed: 2026-05-21
Supersedes: none
Superseded By: none
Stability: provisional
Binding Sources: `contracts/abi/c_api.contract.toml`, `contracts/build/language_baseline.contract.toml`

# C-Compatible ABI Boundary

Dominium implementation now uses C17 and C++17 as the mainline language
baseline. Stable public binary boundaries remain C-compatible.

## Boundary Shape

Stable ABI surfaces use:

- `extern "C"` for C functions consumed by C++
- opaque handles for owned objects
- versioned POD structs with `struct_size`
- explicit allocator or destroy/free functions
- explicit result/refusal codes
- documented callback lifetime, threading, and `void *user` ownership context

Stable ABI surfaces do not expose:

- C++ classes
- templates
- STL containers
- exceptions
- RTTI
- overload-only C++ names
- platform headers in engine public ABI
- raw save/replay/network layout as compiler structs

## Implementation Freedom

C++17 may be used behind the ABI for ownership, resource management, backend
composition, diagnostics, and tooling. That implementation can be replaced
without compatibility promises unless a public surface registry entry promotes
it.

## Relationship To Language Baseline

The language baseline controls how source is compiled. The ABI boundary controls
what downstream products, providers, tools, and modules may rely on. Moving to
C17/C++17 does not make C++ ABI stable.
