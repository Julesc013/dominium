# POST-CONVERGE-10L Next Family Recommendation

Status: DERIVED
Last Reviewed: 2026-05-16

## Recommended Next Task

`POST-CONVERGE-10M - Retired-Domain Path Policy and Tool Hash Drift Remediation`

## Why

Focused RepoX remains at 51 failures and 5 warnings. The distribution/product proof family accounts for 12 failures, but it is not safe to fix by fabricating `archive/generated/dist/bin` wrapper surfaces in this task. The next actionable families are:

- retired-domain path policy checks against `embodiment/`, `geo/`, `diag/`, and `universe`
- tool hash/audit staleness for `tools/xstack/compatx/compatx.py`, `tools/xstack/securex/securex.py`, and identity fingerprint evidence
- RepoX ruleset mapping gaps

POST-CONVERGE-11 should follow only after non-proof RepoX governance failures are reduced or explicitly accepted by a reviewed gate.
