Status: DERIVED
Last Reviewed: 2026-05-16
Supersedes: none
Superseded By: none

# TEST-PERF-00 Blockers

## Remaining

- Focused RepoX still fails from POST-CONVERGE-10K with 51 failures and 5 warnings.
- Full CTest wall-time still needs a complete timing baseline and optional sharding policy.
- Product boot proof and portable projection proof remain separate tasks.

## Classified

- Canonical `verify` CTest discovery can report 0 tests when the build tree is not configured. Configure refresh restores discovery.
- CTest smoke labels were not usable before TEST-PERF-00 because label attachment was not written into the generated CTest metadata.

## Not Blockers For Fast Validation

- Full CTest wall-time does not block T0, focused, or impacted validation.
- RepoX semantic failures do not block the creation of tiered test selection tooling, but they still block product-proof promotion.
