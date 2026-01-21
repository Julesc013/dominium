--------------------------------
OWNERSHIP & RESPONSIBILITY
--------------------------------
ENGINE:
- Deterministic primitives and invariants defined by this spec.
- Implementation lives under `engine/` (public API in `engine/include/`).

GAME:
- None. Game consumes engine primitives where applicable.

TOOLS:
- None. Tools may only consume public APIs if needed.

SCHEMA:
- None (no canonical schema formats defined here).

FORBIDDEN:
- No launcher/setup orchestration logic in engine or game.
- No engine internal headers exposed outside engine targets.
- No game rules or policy implemented inside engine primitives.

DEPENDENCIES:
- Engine -> libs/ and schema/ only (never game/launcher/setup/tools).
- Game -> engine public API and schema/ only.
- Tools -> engine public API, game public API, and schema/ only.
- Launcher/Setup (if applicable) -> libs/contracts + schema (launcher may also use engine public API).
--------------------------------
# SPEC_VM — Deterministic Bytecode VM Constraints

This spec defines constraints for any deterministic bytecode VM used in SIM
(rulepacks, graph queries, compiled evaluation, etc.).

## Scope
Applies to:
- bytecode formats executed in deterministic simulation paths
- VM runtime constraints and budgets
- forbidden behaviors (IO, dynamic allocation, floats)

## Determinism constraints
- Fixed-point only; no float/double instructions.
- Deterministic instruction semantics (no undefined behavior).
- Deterministic memory model:
  - fixed stack size
  - fixed heap/arena reserved before execution
  - no dynamic allocation during execution
- Deterministic endianness and field widths for bytecode decoding.

## Fixed instruction budget
- Execution MUST have a fixed instruction budget per tick (work units).
- Budget consumption MUST be deterministic and independent of wall-clock.
- Exceeding budget MUST yield a deterministic outcome (halt with error code,
  deferred continuation, or deterministic trap), but MUST NOT partially mutate
  authoritative state.

## Forbidden behaviors
- IO (filesystem, network, OS calls) during execution.
- Platform-specific intrinsics or undefined numeric operations.
- Tolerance/epsilon math and floating-point approximations.
- Self-modifying bytecode or reading uninitialized memory.

## Integration rules
- VM results that affect authoritative state MUST be emitted as deltas
  (`docs/SPEC_ACTIONS.md`).
- VM execution is scheduled and budgeted by the SIM scheduler
  (`docs/SPEC_SIM_SCHEDULER.md`).

## Source of truth vs derived cache
**Source of truth:**
- validated bytecode blob + version identifiers
- input packets and committed deltas

**Derived cache:**
- JIT/decoded instruction caches (if any) — must be regenerable and deterministic

## Related specs
- `docs/specs/SPEC_DETERMINISM.md`
- `docs/SPEC_ACTIONS.md`
- `docs/SPEC_SIM_SCHEDULER.md`
- `docs/SPEC_PACKETS.md`

