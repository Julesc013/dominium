# POST-CONVERGE-10O Next Task Decision

Status: DERIVED
Last Reviewed: 2026-05-17

## Decision

Proceed to `POST-CONVERGE-10P - Residual RepoX Governance and Source-Policy Remediation`.

## Rationale

Focused RepoX still has real non-proof hard failures:

- MW-4 embodiment import evaluation failures.
- Missing RepoX ruleset mappings.
- Canon superseded-doc failure.
- Extension registry gap for `capability_overrides`.
- Worldgen retry-loop policy failure.
- Shadow bounded policy failure.

The remaining product/projection proof failures should not circularly block POST-CONVERGE-11 by themselves, but POST-CONVERGE-11 cannot proceed while these non-proof hard failures remain unresolved or unaccepted.

## Not Selected

- POST-CONVERGE-11: blocked by real non-proof RepoX failures.
- POST-CONVERGE-10P warning acceptance ledger only: not sufficient because hard governance failures remain.
- TEST-PERF-00: useful for validation speed, but not a substitute for semantic RepoX disposition.
- CTEST-DISCOVERY-00: not the main blocker because canonical verify discovery reports 493 tests.
