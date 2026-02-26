Status: CANONICAL
Last Reviewed: 2026-02-26
Version: 1.0.0
Scope: MAT-8 causality strictness policy and nothing-just-happens guarantees

# Nothing Just Happens

## Causality Strictness

Causality strictness is a deterministic policy selected by session/scenario configuration.

- `causality.C0`
  - Macro changes are allowed.
  - Provenance events are mandatory.
  - Commitments are optional unless a law or server profile requires them for a category.
- `causality.C1`
  - Meso-continuous behavior is expected.
  - Commitments are mandatory for major categories (construction, logistics, maintenance).
  - Provenance events remain mandatory for all material-impacting macro/meso outcomes.
- `causality.C2` (reserved)
  - Micro actions in declared micro zones require commitments.
  - Enforced micro commitment checks are future-scoped and bounded by ROI/performance policy.

## Core Rule

No macro state change is lawful without:

1. deterministic process execution,
2. provenance event emission,
3. commitment linkage when required by active causality strictness.

This is the MAT constitutional form of the "nothing just happens" guarantee.

## Policy Declaration

Causality strictness is policy-driven and deterministic.

- Recommended declaration point: Scenario/Session policy packs.
- Optional declaration point: UniversePhysicsProfile extensions for universe-wide defaults.

Runtime must resolve strictness from profile/policy data, not hardcoded mode flags.

## Deterministic Refusals

When strictness requires commitments and none is linked, the runtime must refuse with:

- `refusal.commitment.required_missing`

All refusals are explicit, deterministic, and auditable.

## Interactions with Existing Constitutions

- Process-only mutation (canon): macro changes must occur through process execution.
- RS-2 conservation ledger: material/accounting deltas remain ledger-accounted.
- RS-3 time constitution: commitment/event timelines are tick-indexed.
- ED-4 epistemics: strictness and history visibility remain law/lens gated.
