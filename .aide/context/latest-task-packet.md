# AIDE Latest Task Packet

## PHASE

POST-CONVERGE-10N - Tool Hash and Audit Staleness Remediation

## GOAL

Reduce or classify focused RepoX tool hash, identity fingerprint, audit evidence, and generated proof staleness without broad audit regeneration or product/projection proof.

## WHY

After POST-CONVERGE-10M, focused RepoX still contained stale SecureX tool hash evidence, a stale identity fingerprint, and audit evidence warnings. These are integrity/evidence issues and must be distinguished from real policy failures.

## CURRENT RESULT

PARTIAL. Focused `inv_repox_rules` improved from 23 failures / 5 warnings to 20 failures / 5 warnings. Safe canonical evidence refreshes fixed `INV-IDENTITY-FINGERPRINT` and `INV-TOOL-VERSION-MISMATCH`. AuditX stale-output and glossary warnings remain.

## CONTEXT_REFS

- `docs/repo/audits/POST_CONVERGE_10N_TOOL_HASH_AUDIT_STALENESS.md`
- `.aide/reports/POST-CONVERGE-10N-tool-audit-findings.json`
- `.aide/reports/POST-CONVERGE-10N-repox-before-after.json`
- `.aide/reports/POST-CONVERGE-10N-post-converge-11-readiness.md`
- `scripts/ci/check_repox_rules.py`
- `docs/audit/identity_fingerprint.json`
- `docs/audit/security/INTEGRITY_MANIFEST.json`

## IMPLEMENTATION

POST-CONVERGE-10N refreshed only canonical tracked evidence with explicit generators and updated RepoX group cache dependencies so tracked docs/audit evidence read by cached groups invalidates correctly.

## EVIDENCE

- `ctest --preset verify -N` reports 493 tests.
- Focused `ctest --preset verify -R inv_repox_rules --output-on-failure` reports 20 failures / 5 warnings after the safe fixes.
- `python tools/ci/tool_identity_fingerprint.py --repo-root . --check` passes.
- A local SecureX integrity-manifest generation matches the tracked manifest.

## NON_GOALS

- no broad AuditX regeneration
- no root moves, deletes, renames, aliases, move maps, or salvage maps
- no product boot proof
- no portable projection proof
- no package or release generation
- no product/runtime/source behavior changes
- no RepoX/AuditX/TestX weakening

## ACCEPTANCE

- tool/audit failures are classified by evidence family
- safe canonical hash/evidence refreshes are applied
- generated/historical audit warnings are preserved
- focused RepoX before/after counts are recorded
- POST-CONVERGE-11 readiness is explicit
- next family or acceptance gate is recommended

## OUTPUT_SCHEMA

Human-readable reports plus JSON evidence:

- `.aide/reports/POST-CONVERGE-10N-tool-audit-findings.json`
- `.aide/reports/POST-CONVERGE-10N-repox-before-after.json`

## TOKEN_ESTIMATE

Latest packet is intended to stay below the AIDE compact-context budget.

## ALLOWED_PATHS

- AIDE reports/context/ledger
- post-converge and release status docs
- direct audit evidence
- RepoX rule/check implementation directly implicated by tool/audit evidence caching

## FORBIDDEN_PATHS

- product/runtime/source behavior changes
- generated product/projection/package/release artifacts
- root moves, deletes, renames, aliases, or move maps
- broad AuditX output regeneration
- RepoX/AuditX/TestX weakening

## VALIDATION

Focused RepoX was rerun after the safe fixes and remains expected-failing at 20 failures / 5 warnings. Final command details are recorded in `.aide/reports/POST-CONVERGE-10N-validation.md`.

## NEXT

Recommended semantic task: residual RepoX governance/source-policy remediation or explicit RepoX acceptance gate. TEST-PERF follow-up remains appropriate for validation speed.
