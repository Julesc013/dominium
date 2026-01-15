# TRANS/COMPILE (Authoring → Compiled)

Deterministic compilation pipeline for TRANS artifacts.

## Responsibilities
- Convert authored/transient representations into compact compiled forms.
- Enforce canonical ordering and TLV versioning for artifacts.

## Non-responsibilities / prohibited
- No platform file-system assumptions beyond explicit IO layers.
- No gameplay logic.

## Spec
See `docs/SPEC_TRANS_STRUCT_DECOR.md`, `docs/SPEC_PACKETS.md`, and `docs/SPEC_DETERMINISM.md`.

