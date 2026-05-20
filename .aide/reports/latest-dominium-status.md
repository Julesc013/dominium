# Latest Dominium Status

Current task: `REPLACEMENT-PROTOCOL-01`.

Result: PASS_WITH_WARNINGS, pending final commit and post-commit checks.

## Current Green State

- Replacement protocol contracts and schemas exist under `contracts/replacement/**`.
- Replacement validator passes strict mode with 0 findings.
- Fixture validation passes: 4 valid packet fixtures and 4 negative fixtures.
- Initial inventory scans 17,942 tracked files and classifies 1,824
  replacement-like historical/future-candidate files descriptively.
- Replacement kind registry includes 19 provisional kinds.
- Replacement status registry includes 10 provisional statuses.
- Diagnostics registry includes 62 diagnostic codes after replacement additions.
- Refusal registry includes 23 refusal codes after replacement additions.
- Public surface registry includes replacement surfaces and passes with 121 surfaces.
- Fast strict passes: 32/32 commands in 301.437 seconds.

## Current Dependency Debt

- `python tools/validators/repo/check_dependency_directions.py --repo-root . --strict`
  fails by design on existing repo debt.
- Existing dependency-direction debt remains visible.
- No broad exceptions are added by REPLACEMENT-PROTOCOL-01.

## Remaining Blockers

- Historical move/router/repair evidence is inventoried but not converted into
  formal replacement packets.
- Runtime migration and rollback are not implemented.
- Provider runtime, module runtime, Workbench UI, and app behavior are not implemented.
- Version/deprecation law is not implemented yet.
- Existing dependency-direction debt must be repaired or precisely excepted in
  later bounded work.
- Existing ABI warnings remain provisional stable-promotion debt.
- Full CTest remains T4 full/release proof and is not run for this task.
- Feature implementation remains blocked until Foundation Lock closes.

DOE-00 readiness: no.

Feature implementation authorized: no.

Next task: `VERSION-DEPRECATION-LAW-01`.
