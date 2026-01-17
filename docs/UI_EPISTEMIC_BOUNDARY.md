# UI Epistemic Boundary (EPIS0)

UI, HUD, and tools MUST never see authoritative truth.
They MUST consume only capability snapshots and epistemic queries.

## Why the Boundary Exists

- Preserves fog-of-war and uncertainty.
- Prevents UI from leaking hidden state.
- Keeps replay, lockstep, and server-auth outputs consistent.
- Ensures determinism by isolating presentation from simulation.

## How to Add UI Features Correctly

1) Add or reuse a capability in the Epistemic Interface Layer (EIL).
2) Ensure the capability declares required sources and UNKNOWN behavior.
3) Consume the capability snapshot in UI code.
4) Render UNKNOWN/STALE states explicitly.

## Forbidden Patterns

- Direct calls into sim/world APIs.
- Reading ECS containers or authoritative time directly.
- UI-driven inference of hidden data (counts, IDs, or timing).
- Debug exceptions without explicit CI entries.

## Allowed Sources

- Capability snapshots produced by EIL.
- Read-only capability queries (epistemic view).
- UI-only presentation helpers that do not reach into sim state.
