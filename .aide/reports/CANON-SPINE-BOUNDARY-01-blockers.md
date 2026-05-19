# CANON-SPINE-BOUNDARY-01 Blockers

Boundary/import/build blockers for this task are closed.

Remaining blockers are outside this boundary repair:

- Full CTest still has semantic/distribution/projection failures, including hardcoded ID/constants checks, data-to-contract registry path drift, missing moved schema path expectations, XStack/removability debt, generated workspace policy failures, and historical blocker tests.
- `cmake --build --preset verify` remains nonzero only because it runs that full verification target.
- Naming validators still report archive/fixture-only warnings for forbidden historical terms.
- Feature work and DOE-00 remain blocked until full proof closes.
