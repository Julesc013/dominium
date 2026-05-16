# First Wave Plan

## AIDE-ROOT-00 Through AIDE-ROOT-06 Result

The root recycling framework and five inventory waves were generated as no-apply evidence. AIDE-ROOT-06 selected a draft-only first planning candidate.

## Recommended First Planning Candidate

- Root: `ide`
- Subtree: `docs/architecture/IDE_PROJECTIONS.md` moved from `ide/README.md`; `ide/manifests/**` remains deferred
- Risk: low
- Apply allowed: false
- Approval status: not_approved

## Gate Note

AIDE-GATE-01 may authorize `AIDE-MOVE-01-PLAN` only. Move application remains unauthorized.

## AIDE-MOVE-01-PLAN Result

AIDE-MOVE-01-PLAN narrowed the first candidate to `ide/README.md` -> `docs/architecture/IDE_PROJECTIONS.md`. The manifest schema/examples under `ide/manifests/**` remain deferred. The plan is draft, not approved, and no-apply. `AIDE-GATE-02` may inspect the plan; move application remains unauthorized.

## AIDE-GATE-02 Result

AIDE-GATE-02 passed with warnings and authorizes only `AIDE-MOVE-01-APPLY` for `ide/README.md` -> `docs/architecture/IDE_PROJECTIONS.md`. All other moves remain unauthorized, and `ide/manifests/**` remains deferred.

## AIDE-MOVE-01-APPLY Result

AIDE-MOVE-01-APPLY moved `ide/README.md` to `docs/architecture/IDE_PROJECTIONS.md` and applied only the six planned reference rewrites. `ide/manifests/**` remains deferred and untouched, the `ide/` root exception was not retired, and the next recommended task is `AIDE-GATE-03`.

## AIDE-GATE-03 Result

AIDE-GATE-03 passed with warnings and verified the first move wave post-state. `AIDE-MOVE-02-PLAN` may proceed, but no move application is authorized.

## AIDE-MOVE-02-PLAN Result

AIDE-MOVE-02-PLAN reviewed the next preferred roots and did not select a second move candidate. After the IDE README move, the remaining preferred-root material is deferred machine-readable IDE metadata or active Python/tooling code. The draft plan is not approved, apply remains false, and the recommended next task is candidate refinement rather than an apply gate.
