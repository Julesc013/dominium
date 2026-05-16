# First Wave Plan

## AIDE-ROOT-00 Through AIDE-ROOT-06 Result

The root recycling framework and five inventory waves were generated as no-apply evidence. AIDE-ROOT-06 selected a draft-only first planning candidate.

## Recommended First Planning Candidate

- Root: `ide`
- Subtree: ide/README.md and ide/manifests projection docs/examples
- Risk: low
- Apply allowed: false
- Approval status: not_approved

## Gate Note

AIDE-GATE-01 may authorize `AIDE-MOVE-01-PLAN` only. Move application remains unauthorized.

## AIDE-MOVE-01-PLAN Result

AIDE-MOVE-01-PLAN narrowed the first candidate to `ide/README.md` -> `docs/architecture/IDE_PROJECTIONS.md`. The manifest schema/examples under `ide/manifests/**` remain deferred. The plan is draft, not approved, and no-apply. `AIDE-GATE-02` may inspect the plan; move application remains unauthorized.

## AIDE-GATE-02 Result

AIDE-GATE-02 passed with warnings and authorizes only `AIDE-MOVE-01-APPLY` for `ide/README.md` -> `docs/architecture/IDE_PROJECTIONS.md`. All other moves remain unauthorized, and `ide/manifests/**` remains deferred.
