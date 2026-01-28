# Piracy Containment (TESTX3)

Status: binding.
Scope: piracy definition and containment without DRM.

## Core invariants
- INVARIANT: AUTH3-PIRACY-006 — Piracy contained by authority, not DRM.
- INVARIANT: AUTH3-AUTH-001 — Authority gates actions only.

## Definition
Piracy is unauthorized durable value extraction.
Copying binaries/content is not piracy under this definition.

## Containment strategy (no DRM)
- server-side authority validation
- entitlement-driven authority issuance
- refusal of durable actions
- explicit upgrade paths

Forbidden:
- engine DRM
- simulation degradation
- encrypted core data
- hidden penalties
- annoyance-based enforcement

Offline piracy yields base_free authority only.
This is intentional and acceptable.

## Cross-references
- `docs/arch/AUTHORITY_AND_ENTITLEMENTS.md`
- `docs/arch/DEMO_AND_TOURIST_MODEL.md`
