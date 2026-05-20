Status: DERIVED
Last Reviewed: 2026-05-20
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: API-ABI-CANON, COMPATIBILITY-CORPUS, PORTABILITY-MATRIX
Binding Sources: `contracts/abi/c_api.contract.toml`, `contracts/abi/abi_rule.registry.json`

# C89 Public API Standard

## Scope

This standard applies to stable C-compatible public headers and ABI-facing
fixtures. Provisional headers may carry warnings, but warnings block stable ABI
promotion until resolved or explicitly excepted.

## Rules

- Use include guards or `#pragma once`.
- Keep public headers self-contained where practical.
- Use `extern "C"` guards when C headers are consumed by C++.
- Avoid mixed declarations and statements in strict C89-facing code.
- Avoid compiler-specific extensions in public ABI.
- Use `domino_` for reusable public symbols and `dominium_` for product public
  symbols.
- Use `DOMINO_` and `DOMINIUM_` for public constants and macros.
- Use opaque handles for owned objects crossing ABI boundaries.
- Include `struct_size` on ABI-visible config, options, descriptor, args, and
  vtable structs.
- Include `api_version` where forward/backward compatibility is required.
- Return explicit result or refusal codes.
- Pair owned allocations with explicit destroy/free functions or explicit
  allocator contracts.
- Carry `void *user` through public callback APIs.

## Example Shape

```c
#ifndef DOMINO_EXAMPLE_H
#define DOMINO_EXAMPLE_H

#ifdef __cplusplus
extern "C" {
#endif

typedef struct domino_example domino_example_t;

typedef struct domino_example_config {
    unsigned int struct_size;
    unsigned int api_version;
    void *user;
} domino_example_config_t;

int domino_example_create(const domino_example_config_t *config,
                          domino_example_t **out_example);
void domino_example_destroy(domino_example_t *example);

#ifdef __cplusplus
}
#endif

#endif
```

## Deferrals

Fixed-width type policy continues to use existing project typedefs until a later
portability matrix task records the final cross-toolchain type surface.
