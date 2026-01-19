# LONG_TERM_SUPPORT_POLICY (FINAL0)

Status: draft  
Version: 1

## Purpose
Define long-term support rules that keep Dominium deterministic and compatible
for decades without relying on informal discipline.

## Versioning policy
### Engine (ABI)
- Public engine headers are ABI-bound.
- Any ABI-affecting change requires explicit ABI notes in this policy doc.
- ABI changes must include: reason, affected headers, and migration impact.

### Game rules
- Game rules are versioned by feature epochs (see `docs/FEATURE_EPOCH_POLICY.md`).
- Sim-affecting changes must bump the relevant epoch.

### Schemas
- Schema changes must follow DATA0/DATA1 governance.
- Major schema bumps require explicit migration or refusal paths.

## Support windows
- Deprecated features remain supported for a minimum of two minor releases.
- Removal requires a documented deprecation window and migration notes.

## Breaking change definition
A breaking change includes:
- ABI changes in engine public headers.
- Sim-affecting semantic changes without an epoch bump.
- Schema major version changes without migration/refusal.

## Required records
Breaking changes MUST update:
- `docs/COMPATIBILITY_PROMISES.md`
- `docs/FEATURE_EPOCH_POLICY.md` (if sim-affecting)
- `docs/RENDER_BACKEND_LIFECYCLE.md` (if backend lifecycle changes)
- This document’s ABI notes section (engine ABI changes)

## Prohibitions
- Silent breaking changes.
- Untracked ABI changes.
- Removing compatibility without explicit refusal paths.
