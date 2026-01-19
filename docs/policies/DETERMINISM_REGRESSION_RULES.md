# Determinism regression rules (machine-checkable)

This file defines deterministic-core guardrails intended to prevent silent
regressions in ordering, hashing, replay, and budgets.

These rules are **semantics-free**: they constrain *how* the engine evolves and
verifies state, not what the state “means”.

## Scan-enforced subset

The following rules are enforced by `tools/ci/arch_checks.py` (via the
`check_arch` target):

**Scope (deterministic core only)**
- `engine/modules/core/**`
- `engine/modules/sim/**`
- `engine/modules/world/**`
- `game/core/**`
- `game/rules/**`
- `game/economy/**`

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
