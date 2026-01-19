# SPEC_PACKING_AND_DELTAS (ECSX0)

Schema ID: ECS_PACKING_DELTAS  
Schema Version: 1.0.0  
Status: binding.  
Scope: serialization, packing, and delta encoding rules for components.

## Purpose
Define deterministic serialization and delta encoding rules that are driven by
component schema and independent of storage layout.

## Serialization Rules
- Deterministic field order: ascending `field_id`.
- Explicit version tags on every component record.
- Skip-unknown safe: preserve unknown fields on read/write.
- Endian policy: little-endian for all on-disk and network encodings.
- No platform-dependent alignment or padding.

## Delta Encoding
Delta encoding is schema-driven:
- Fields may declare `delta_hints` (baseline group, quantization hint).
- Baselines are explicit and deterministic.
- Authoritative fields must **not** use float quantization.
- Fixed-point quantization is allowed only with explicit scale and rounding rules.

Forbidden:
- "first writer wins" nondeterminism.
- unordered merge without normalization.

## Packing Rules
Bitfield packing is allowed only when:
- field semantics are preserved,
- extraction is deterministic and documented,
- packing is independent of compiler bitfield layout.

Packed views:
- are derived by default,
- must not be treated as authoritative unless explicitly declared.

## Determinism Constraints
Authoritative fields:
- must use integer or fixed-point types only,
- must avoid platform-dependent types or float math.

Derived/presentation fields:
- may use floats or quantized data,
- must not affect authoritative state or hashes.

## Examples (Conceptual)
```
field_id=2 (count: U32) -> delta by subtraction from baseline
field_id=3 (morale_q16: I32) -> fixed-point delta with scale=1/65536
field_id=9 (ui_color_tag: U32) -> optional derived-only packing
```
