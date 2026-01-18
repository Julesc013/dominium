# CIV2 Governance, Legitimacy, and Jurisdictions

This document defines the CIV2 governance substrate: jurisdictions, legitimacy,
enforcement capacity, and policy scheduling. All updates are deterministic and
event-driven.

## Core components

- Jurisdictions (`schema/governance/SPEC_JURISDICTIONS.md`)
  - Explicit boundaries and default standards.
  - next_due_tick required for governance events.
- Legitimacy (`schema/governance/SPEC_LEGITIMACY.md`)
  - Fixed-point value updated by scheduled events only.
  - Thresholds define stable/contested/failed regimes.
- Enforcement capacity (`schema/governance/SPEC_ENFORCEMENT.md`)
  - Bounded capacity required for policy execution.
- Policies (`schema/governance/SPEC_POLICY_SYSTEM.md`)
  - ACT/T4 schedules with deterministic ordering.
- Standards resolution (`schema/governance/SPEC_STANDARD_RESOLUTION_GOV.md`)
  - Order: explicit -> org -> jurisdiction -> personal -> fallback.

## Event-driven governance

- No per-tick polity scans.
- Jurisdictions and policies expose next_due_tick.
- Legitimacy updates are scheduled events (tax/service hooks).

## Epistemic constraints

Policy knowledge and legitimacy values are epistemic.
UI must not show omniscient government dashboards.

## CI enforcement

The following IDs in `docs/CI_ENFORCEMENT_MATRIX.md` cover CIV2:

- CIV2-JURIS-DET-001
- CIV2-NEXTDUE-001
- CIV2-LEGIT-DET-001
- CIV2-POLICY-T4-001
- CIV2-STAND-RES-001
- CIV2-EPIS-001
