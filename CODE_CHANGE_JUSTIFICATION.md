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
