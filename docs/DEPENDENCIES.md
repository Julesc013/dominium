# Dependencies (Allowed / Forbidden)

This document defines the **allowed dependency directions** between major
subsystems. It complements:
- Layout contract: `docs/DIRECTORY_CONTEXT.md`
- Language/determinism constraints: `docs/LANGUAGE_POLICY.md`, `docs/SPEC_DETERMINISM.md`

## High-Level Graph
Allowed (→):
- `dominium` → `domino`
- `domino` → `domino/system` (platform abstractions)
- `tools` → `domino`, `dominium`
- `tests` → `domino`, `dominium`

Forbidden (✗):
- `domino` → `dominium` (engine must not depend on product layer)
- Deterministic simulation code → OS/platform APIs (see `docs/LANGUAGE_POLICY.md`)
- Public headers (`include/**`) → private implementation headers (`source/**`)

## Public Header Rules
- Headers under `include/**` are contracts; they must be self-contained and include only what they need.
- Do not include `source/**` headers from `include/**` or across module boundaries.
- ABI-visible structures and interfaces follow `docs/SPEC_ABI_TEMPLATES.md`.

## Determinism Boundary
- Non-deterministic sources (wall clock time, OS randomness, platform input timing, floating point)
  must not affect authoritative simulation outcomes. See `docs/SPEC_DETERMINISM.md`.

## External/Vendored Code
- Vendored third-party sources (e.g., `external/**`) are treated as external dependencies.
- Prefer wrapping external APIs behind a Domino/Dominium façade rather than leaking them through public headers.

