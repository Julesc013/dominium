Status: DERIVED
Last Reviewed: 2026-02-01
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: DOC-CONVERGENCE
Replacement Target: patched document aligned to current canon ownership and release scope

# Onboarding Guide (UX-1)

## Patch Notes

- Current status: partially aligned to the Constitutional Architecture and release-freeze documentation set.
- Required updates: documentation surface exists, but current canon ownership is not explicit
- Cross-check with: `docs/audit/CANON_MAP.md` and `docs/audit/DOC_DRIFT_MATRIX.md`.


Onboarding must teach the system model, not hide it. Missing packs, refusals, and capability gaps are part of the user experience and must be explained clearly.

## First-Run Messages
- Content packs are optional.
- Worlds can be created with minimal data.
- Refusals are deterministic outcomes, not crashes.

## Profiles
Profiles guide presentation and recommendations only:
- Casual: guided defaults, higher verbosity.
- Hardcore: minimal UI, explicit refusals.
- Creator: deep inspectors and diagnostics.

Profiles never alter simulation outcomes.

## Refusals
Refusal presentation must include:
- Stable symbolic name
- Human-readable explanation
- Structured details (expandable)
- Suggested data-side fixes when possible

## Next Steps
- Validate packs with `pack_validate`.
- Inspect refusals with `refusal_explain`.
- Compare outcomes with `replay_diff`.
