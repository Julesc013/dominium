Status: CANONICAL
Last Reviewed: 2026-03-12
Scope: ARCH-AUDIT-0
Binding Sources: `docs/canon/constitution_v1.md`, `docs/canon/glossary_v1.md`

# Model Purity Audit Constitution

## Purpose
Define the deterministic architectural audit that prevents presentation data, duplicated meaning, hidden nondeterminism, and ungoverned stability drift from entering release builds.

## A. Truth Purity
- Canonical Truth state may store assemblies, fields, law-governed process state, provenance anchors, contract pins, and other semantic state only.
- Canonical Truth state must not store sky gradients, starfield points, moon phase presentation values, lighting buffers, shadow buffers, water render state, or equivalent presentation payloads.
- Derived artifacts may carry presentation payloads when they are explicitly marked as derived and regenerable.

## B. Derivation Discipline
- Visual and UX output must be produced from lens, projection, view, and renderer-facing derived artifacts.
- Renderer modules must consume `RenderModel` or equivalent derived view surfaces only.
- Renderer code must not read `TruthModel`, `UniverseState`, or process runtime state directly.

## C. Single Source Of Meaning
- Capability negotiation must have one authoritative semantic engine.
- Overlay merge must have one authoritative semantic engine.
- Illumination semantics must resolve through one authoritative model pipeline.
- Deterministic ID generation must have one authoritative engine per identity family.
- Wrappers, probes, and replay tools may call authoritative engines, but they must not silently fork the semantics.

## D. Determinism Discipline
- Truth paths must not depend on wall-clock time.
- Truth paths must not use unnamed RNG sources.
- Truth paths must not rely on unordered container iteration for authoritative ordering.
- Truth math must not depend on floating-point semantics unless the path is explicitly reviewed as a deterministic approximation or fixed-point bridge.
- Any reviewed exception must remain explicit in the audit report and baseline.

## E. Stability Markers
- Registry entries in the governed META-STABILITY scope must carry stability markers.
- Provisional entries must declare `future_series` and `replacement_target`.
- Stable entries must declare `contract_id`.
- Stable semantic drift without a contract bump is a release blocker.

## F. Compatibility Discipline
- `UniverseIdentity` and session boot artifacts must pin the contract bundle.
- Strict pack loading must require pack compatibility manifests.
- Negotiation records must be logged for governed connection flows.

## Blocking Policy
- Presentation-in-truth findings are blocking.
- Renderer truth leaks are blocking.
- Duplicate authoritative semantic definitions are blocking.
- Hidden wall-clock or unnamed RNG use in truth paths is blocking.
- Missing stability markers or missing contract pins in governed scope are blocking.
- Reviewed, deterministic approximation or ordering exceptions may be recorded as known exceptions for ARCH-AUDIT-1, but they must never be hidden.
