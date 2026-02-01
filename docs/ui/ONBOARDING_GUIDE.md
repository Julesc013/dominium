Status: DERIVED
Last Reviewed: 2026-02-01
Supersedes: none
Superseded By: none

# Onboarding Guide (UX-1)

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