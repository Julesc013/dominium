# Contracts (Public Header API Rules)

This document defines the **API contract conventions** used by public headers in
`include/domino/**` and `include/dominium/**`. It is referenced by per-symbol
doc blocks to avoid repeating the same rules across headers.

## Scope
- Applies to declarations in `include/**` that are consumed across translation
  units and/or module boundaries.
- Does not replace subsystem specs under `docs/SPEC_*.md`; those specs remain
  the canonical home for behavioral rules and invariants.

## Call Conventions
### Parameters
- **Direction** is documented as:
  - `in`: caller-provided input; callee must not retain ownership unless stated.
  - `out`: caller-provided storage written by callee.
  - `inout`: both read and written.
- **Ownership**:
  - Pointer parameters are **not** owned by the callee unless explicitly stated.
  - Returned pointers are either:
    - **borrowed** (points into internal/static storage), or
    - **owned** (caller must release via the matching `*_destroy`/`*_free` API).
    The header must state which.
- **Nullability**:
  - Each pointer parameter must state whether it is optional.
  - If not stated, treat the pointer as **required** by the contract.

### Return Values / Errors
- No exceptions are used across the C/C++ boundary (`docs/LANGUAGE_POLICY.md`).
- APIs document failure signaling explicitly per function. Common patterns:
  - `bool`: `true` success / `false` failure.
  - pointer: non-NULL success / `NULL` failure.
  - id/handle typedefs: non-zero success / `0` failure (when the type reserves 0).
  - status enums (e.g., `dom_status`): explicit enumerators.
- If an API uses an OS error code or platform status, it must document the
  mapping and whether the value is stable across platforms.

## Data/ABI Rules
- Public structs are **POD-only** across module boundaries (no C++ types, no STL).
- If a struct is intended for cross-module ABI use, it must be **versioned and
  size-stamped** as described in `docs/SPEC_ABI_TEMPLATES.md`.
- Do not rely on raw `memcmp()` of public structs for determinism or hashing
  unless the spec explicitly permits it (`docs/SPEC_DETERMINISM.md`).

## Thread-Safety and Determinism
- Thread-safety is **explicitly documented** per API. If not stated, assume:
  - no internal synchronization; callers must serialize access.
- Determinism requirements are subsystem-specific:
  - Deterministic simulation code must follow `docs/SPEC_DETERMINISM.md`.
  - UI/platform/tools layers are not required to be deterministic, but must not
    feed nondeterministic sources into authoritative simulation decisions.

## Documentation Placement (No Duplication)
- Each public symbol is documented **exactly once**, in the public header that
  declares it.
- Source files (`source/**`) may add comments only for internal invariants,
  rationale, and non-obvious algorithms; they must not restate header contracts.

