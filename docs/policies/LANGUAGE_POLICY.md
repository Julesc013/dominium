Status: DERIVED
Last Reviewed: 2026-02-01
Supersedes: none
Superseded By: none

# Dominium — Language Policy (Authoritative)

This document defines mandatory language/toolchain constraints. Determinism
behavioral requirements are specified in `docs/specs/SPEC_DETERMINISM.md` and guarded
by `docs/policies/DETERMINISM_REGRESSION_RULES.md`.

## 1. C90 rules (deterministic engine core)
Applies to code that participates in deterministic simulation outcomes, replay,
or world hashing (the deterministic core).

Build contract:
- Must compile as C90 (`CMAKE_C_STANDARD 90`, extensions off).
- Do not use C99/C11 language features (VLAs, designated initializers, mixed
  declarations/statements, `//` comments, etc.).

Type policy:
- Prefer project-defined fixed-width and fixed-point types:
  - `engine/include/domino/core/types.h` (`u32`, `i32`, `d_bool`, etc.)
  - `engine/include/domino/core/fixed.h` / `engine/include/domino/dnumeric.h` (fixed-point Q types)
- If `<stdint.h>`/`<stdbool.h>` appear in non-deterministic glue or public façade
  headers, deterministic serialization/hashing MUST still encode fields
  explicitly and MUST NOT hash raw struct bytes.

Forbidden in deterministic core (non-exhaustive):
- floating-point math (`float`/`double`) in deterministic paths
- OS/platform time sources (`time()`, `clock()`, wall clock)
- platform headers and platform-dependent APIs
- dynamic allocation in deterministic tick loops (unless explicitly specified)

## 2. C++98 rules (product/non-core modules)
Applies to non-deterministic runtime/product layers (e.g. `game/**`, `launcher/**`,
`setup/**`, `client/**`, `server/**`, `tools/**`) and optional tooling where
determinism is not part of the simulation contract.

Rules:
- Must compile as C++98.
- No exceptions, no RTTI.
- Do not expose STL types across C ABI boundaries.

## 3. Boundary rule (hard)
Deterministic simulation code MUST NOT depend on platform/system/render/UI code
as an input to simulation decisions. Platform and rendering layers may exist to
host the runtime loop and display derived state, but they must not mutate or
influence authoritative simulation state outside of the intent/delta contracts.