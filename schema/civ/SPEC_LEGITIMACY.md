--------------------------------
OWNERSHIP & RESPONSIBILITY
--------------------------------
ENGINE:
- Stable IDs, deterministic scheduling primitives.
GAME:
- Legitimacy modeling, decay, and enforcement impact.
SCHEMA:
- Legitimacy record formats and validation constraints.
TOOLS:
- Inspectors/editors only (no runtime behavior).
FORBIDDEN:
- No runtime logic in schema specs.
- No legitimacy without explicit support signals.
DEPENDENCIES:
- Engine -> (no dependencies outside engine/).
- Game -> engine public API only.
- Schema -> none (formats only).
- Tools -> schema + engine/game public APIs only.
--------------------------------
# SPEC_LEGITIMACY — Legitimacy Canon (CIV0+)

Status: draft
Version: 1

## Purpose
Define legitimacy as a measurable acceptance/compliance/stability signal that
affects enforcement capacity and institutional resilience.

## Required fields
- legitimacy_id (stable, unique within a timeline)
- subject_ref (institution or governance context)
- domain_ref (spatial scope)
- score (normalized numeric value)
- components (explicit sub-scores)
- decay_policy_ref (ACT-based decay behavior)
- provenance_refs (origin and causal chain)

Optional fields:
- thresholds (enforcement tiers)
- support_sources (consent, performance, coercion)
- audit_refs (legitimacy audit configuration)

## Rules (absolute)
- Legitimacy must be derived from explicit, auditable signals.
- Legitimacy decays deterministically when support is absent.
- Governance enforcement capacity is bounded by legitimacy.

## Integration points
- Governance: `schema/civ/SPEC_GOVERNANCE.md`
- Institutions: `schema/civ/SPEC_INSTITUTIONS.md`
- Time: `schema/time/README.md`
- Authority: `schema/authority/README.md`

## See also
- `docs/arch/GOVERNANCE_AND_INSTITUTIONS.md`
