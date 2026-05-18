# POST-CONVERGE-10G Product Boot Readiness

Status: BLOCKED

## Decision

POST-CONVERGE-11 is not ready yet.

## Reason

Focused tuple `inv_repox_rules` still fails after safe remediation. The count was reduced from 1844 failures to 1769 failures, but the remaining failures include broad canonical documentation status drift, missing canon-index acceptance, historical reference debt, missing contract registry acceptance, product descriptor distribution blockers, and retired-domain path policy checks.

## Accepted Progress

- `invariant_units_present` remains fixed from POST-CONVERGE-10F.
- RepoX no longer reports the stale top-level root structure family fixed in 10G.
- RepoX no longer reports stale root-level `appshell/` expectations; AppShell checks now use `runtime/shell/`.
- RepoX group cache now depends on the rule implementation, preventing stale cached rule results after rule changes.

## Remaining Gate

`POST-CONVERGE-11 - Product Boot Proof With Native Binaries` must wait until focused RepoX either passes or its remaining semantic failures are dispositioned by a stricter, reviewed blocker task. Move/apply authorization remains false.
