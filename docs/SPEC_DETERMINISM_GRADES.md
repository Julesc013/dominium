# SPEC_DETERMINISM_GRADES — D0/D1/D2 Model (Authoritative)

This spec defines a determinism grading system for runtime subsystems and
backends selected at launch time (system/platform, rendering, audio IO, etc.).
It complements `docs/SPEC_DETERMINISM.md`, which defines the deterministic core
contract for simulation, replay, and hashing.

## 1. Grades

### D0 — Bit-exact
**Definition:** Given the same authoritative inputs and deterministic command
stream, the backend produces bit-identical outputs across supported platforms
and toolchains.

**Required for:**
- lockstep/rollback authoritative simulation
- per-tick world hashing used to validate replay/lockstep
- any backend that can affect authoritative decisions

**Notes:**
- D0 is a *strong* guarantee; “usually matches” is not D0.
- D0 backends must avoid platform-dependent floating point, unordered iteration,
  and dependence on wall-clock time or OS state (see `docs/SPEC_DETERMINISM.md`).

### D1 — Tick-exact
**Definition:** Authoritative simulation results (tick-by-tick) match across
platforms, but some non-authoritative outputs may differ bitwise (e.g. debug
telemetry, optional metrics, presentation-only intermediates).

**Allowed only when:**
- the differing outputs are not hashed for replay verification
- the differing outputs cannot feed back into authoritative simulation state

### D2 — Best-effort
**Definition:** Outputs may differ across machines/toolchains. The backend is
not considered deterministic for correctness purposes.

**Allowed only when:**
- the backend is strictly non-authoritative (presentation-only, tooling-only)
- any influence on authoritative simulation is structurally prevented by the
  architecture (intent/delta boundaries, no cross-layer mutation)

## 2. Enforcement rules

### 2.1 Lockstep requires D0 (no silent downgrade)
When launching in lockstep-strict mode:
- every subsystem marked **lockstep-relevant** MUST select a D0 backend
- selection MUST NOT silently downgrade a lockstep-relevant subsystem to D1/D2
- if no D0 backend is selectable, the launch MUST fail with a clear error

### 2.2 Explicit overrides must still satisfy requirements
If the user explicitly overrides a backend (e.g. `--sys.fs=win32` or `--gfx=dx11`)
and the chosen backend violates lockstep-strict requirements, the launcher MUST:
- reject the configuration with a clear error, or
- select a compatible D0 fallback *only if* an explicit policy permits it and
  the selection is logged (no invisible changes)

### 2.3 Optimized paths must have a D0 fallback
If a “perf” backend uses non-D0 techniques (platform APIs, SIMD variance, float,
driver behavior, etc.), the subsystem MUST provide a D0-compatible fallback
backend that can be selected under lockstep-strict operation.

This is the “no dead-end optimization” rule: optimized code paths are allowed
only when deterministic operation remains possible.

## 3. Golden replay hashing requirement (hook only)

Replays that participate in determinism verification MUST record:
- the determinism grade requirements in effect (e.g. lockstep-strict on/off)
- the selected backend identity per subsystem (backend name/id + ABI versions)
- a deterministic “selection signature” sufficient to detect mismatches

At playback time, the runtime MUST be able to:
- compare recorded selection signature vs the current selection
- report mismatches clearly (tests and strict policy wiring land in later prompts)

