# WORLD/DOMAIN (Domains)

World domains partition authoritative state for stability, scaling, and replay.

## Responsibilities
- Stable domain IDs and canonical domain ordering.
- Domain-local storage boundaries and deterministic iteration rules.

## Non-responsibilities / prohibited
- No gameplay semantics; domains are structural partitions.
- No derived caches presented as source-of-truth.

## Spec
See `docs/SPEC_DOMAINS_FRAMES_PROP.md` and `docs/SPEC_DETERMINISM.md`.

