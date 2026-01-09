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
- `docs/SPEC_DGFX_IR_VERSIONING.md`
- `docs/SPEC_DETERMINISM.md`
