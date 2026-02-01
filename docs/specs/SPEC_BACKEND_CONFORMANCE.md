Status: DERIVED
Last Reviewed: 2026-02-01
Supersedes: none
Superseded By: none

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
# SPEC_BACKEND_CONFORMANCE — Renderer/Platform Conformance

This spec defines structural conformance requirements for DGFX backends and
platform input backends. Conformance is **structural**, not pixel-perfect.

## 1. Scope
- DGFX backends must be deterministic for accepted command streams.
- Platform input backends must normalize event ordering deterministically.
- Rendering and input are derived-only and must not affect sim hash.

## 2. DGFX conformance requirements
Backends MUST:
- accept or reject IR commands deterministically based on declared caps,
- skip unknown commands without desynchronizing the stream,
- produce trace metrics that match the reference backend for supported ops.

Conformance is evaluated using trace capture:
- accepted command count
- rejected command count
- primitive counts
- aggregate bounding boxes
- text glyph counts (when text is supported)

The software backend is the reference for structural traces.

## 3. Capability claim correctness
If a backend claims a capability:
- it MUST accept the corresponding IR commands.

If a backend does not claim a capability:
- it MUST reject the corresponding IR commands deterministically.

## 4. Input ordering conformance
Input backends MUST:
- normalize event ordering deterministically,
- preserve relative ordering within a single poll batch,
- produce identical normalized traces for equivalent event sequences.

## 5. No-modal-loading invariants
Backend submission and present operations MUST:
- avoid blocking beyond configured thresholds,
- emit timing trace events for conformance tests,
- never stall the UI or render loop.

## 6. Related specs
- `docs/specs/SPEC_DGFX_IR_VERSIONING.md`
- `docs/specs/SPEC_DETERMINISM.md`