# Determinism regression rules (machine-checkable)

This file defines deterministic-core guardrails intended to prevent silent
regressions in ordering, hashing, replay, and budgets.

These rules are **semantics-free**: they constrain *how* the engine evolves and
verifies state, not what the state “means”.

## Scan-enforced subset

The following rules are enforced by the build test `domino_det_regression_scan_test`
(see `source/tests/determinism_regression_scan_test.c`):

**Scope (deterministic core only)**
- `source/domino/sim/**`
- `source/domino/world/**`
- `source/domino/trans/**`
- `source/domino/struct/**`
- `source/domino/decor/**`
- `source/domino/agent/**`
- `source/domino/core/**` (excluding known non-deterministic/debug helpers)

**Forbidden patterns**
- No floating point: tokens `float`, `double` (covers `long double` as well)
- No non-deterministic RNG: calls to `rand(` / `srand(`
- No OS time sources: calls to `time(` / `clock(` and includes of `<time.h>`
- No platform headers in deterministic core: includes of `<windows.h>`, `<unistd.h>`, `<sys/time.h>`
- No unordered C++ containers in deterministic core: includes of `<unordered_map>`, `<unordered_set>`

## Additional rules (documented, not fully enforced yet)

These are intentionally written to be mechanically testable, but are not yet
covered by the scan tool:

- No hashing raw memory blocks (no hashing of struct bytes with padding).
- No hashing pointer addresses.
- No container iteration without explicit canonical sort.
- All graph adjacency iterators are canonical and stable.
- All promotion/demotion decisions are based on canonical interest volumes.
- All authoritative state mutation occurs via delta commit ordering.

## Non-negotiable eligibility rule

Any system that cannot be hashed, replayed, budgeted, and ordered canonically is
not eligible to exist in the engine core.

