# Code Change Justifications (GOV0)

Status: binding for engine/game code changes.

Use this log whenever engine/ or game/ code is modified. Each entry must answer:
Why can this not be data?

## Entries

### 2026-01-29 — DETER-0 determinism hard locks

Touched: engine/, game/, tools/

Reason: Enforce named RNG streams, deterministic reduction order, and deterministic seed derivation.

Why can this not be data? Determinism enforcement and RNG stream derivation must occur inside
authoritative execution paths and cannot be expressed solely via data packs or schemas.

### 2026-01-29 — PLATFORM/RENDERER modular backends + deterministic dir ordering

Touched: engine/, docs/architecture/

Reason: Implement modular platform backends (win32/posix/sdl2 stubs) and capability-gated renderer backends
with deterministic directory iteration and presentation-only behavior.

Why can this not be data? Platform and renderer integration is OS/runtime code that cannot be represented
as data packs; deterministic filesystem iteration and backend dispatch must be enforced in code.

### 2026-01-29 — SCALE collapse/expand type forward declaration fix

Touched: game/

Reason: Ensure dom_scale_capsule_data is declared before use so scale collapse/expand compiles cleanly.

Why can this not be data? This is a compile-time type safety fix inside authoritative code and cannot be
expressed or corrected via data packs or schemas.
