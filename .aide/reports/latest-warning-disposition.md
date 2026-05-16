# Latest Warning Disposition

Status: DERIVED
Last Reviewed: 2026-05-17
Supersedes: none
Superseded By: none

## TEST-PERF-00

- Focused tuple RepoX still fails.
- Canonical `ctest --preset verify -N` discovered 0 tests before configure refresh, then 493 tests after `cmake --preset verify`.
- CTest smoke labels now discover 57 tests after `dom_add_testx` label repair and reconfigure.
- Full CTest, product boot proof, package proof, and portable projection proof remain not run by TEST-PERF-00.
- Full CTest remains a promotion gate rather than the normal post-change feedback path.

## POST-CONVERGE-10L

- Focused RepoX remains 51 failures / 5 warnings.
- The 12 distribution/product target failures are classified as missing portable projection wrapper/proof surfaces under `dist/bin`.
- Missing product/projection proof remains blocking and was not converted into a warning.

## POST-CONVERGE-10M

- Focused RepoX remains expected-failing but improved to 23 failures / 5 warnings.
- The safe retired-domain stale rule path family was fixed, not converted into warnings.
- Two source import blockers remain for MW-4 fixture evaluation through stale `embodiment.*` lazy imports.

## POST-CONVERGE-10N

- Focused RepoX remains expected-failing but improved to 20 failures / 5 warnings.
- `INV-IDENTITY-FINGERPRINT` and `INV-TOOL-VERSION-MISMATCH` hard failures were fixed by canonical evidence refresh, not converted into warnings.
- `INV-AUDITX-OUTPUT-STALE` remains a warning because broad AuditX output regeneration was out of scope.
- Four `WARN-GLOSSARY-TERM-CANON` warnings in generated/historical audit evidence remain warnings and were not rewritten.
- Product boot proof, package proof, release proof, portable projection proof, build, and full CTest were not run by scope.

## POST-CONVERGE-10O

- Focused RepoX remains expected-failing at 20 failures / 5 warnings.
- The remaining hard failures were not accepted as warnings.
- POST-CONVERGE-11 remains blocked because real non-proof governance/source-policy failures remain.
- The warning candidates are still `INV-AUDITX-OUTPUT-STALE` and four generated/historical glossary warnings.
- Product boot proof, package proof, release proof, portable projection proof, build, and full CTest were not run by scope.

## POST-CONVERGE-11

- Focused RepoX remains expected-failing at 20 failures / 5 warnings.
- The remaining hard failures were not accepted as warnings.
- Product binaries were not inspected or executed because the RepoX readiness gate failed.
- POST-CONVERGE-12 remains blocked because product boot proof did not run.
- Product boot proof, package proof, release proof, portable projection proof, build, and full CTest were not run by scope.

## POST-CONVERGE-12

- Product boot proof remains blocked and was not accepted as sufficient portable projection input.
- No projection root was generated and no projection validator was run.
- The remaining RepoX hard failures were not accepted as warnings.
- RELEASE-00 remains blocked until RepoX/product boot/projection gates are resolved or explicitly accepted.
