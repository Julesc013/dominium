# Q33 ExecPlan

## Objective

Import portable Q31 AIDE Lite governance into Dominium without copying AIDE
source state or bloating Dominium doctrine into AIDE memory.

## Scope

Allowed writes stay under `.aide/**`, compact root guidance, and optional
`docs/reference/aide-governance-sync.md`. Product/source and doctrine roots are
read-only except for inspection.

## Steps

1. Record baseline Git, AIDE Lite, source-pack, and doctrine state.
2. Review the canonical Q31 pack and dry-run import.
3. Use targeted sync for portable governance files because direct import has
   target-local conflicts.
4. Preserve Dominium-specific memory, queue evidence, doctrine refs, and manual
   `AGENTS.md` content.
5. Generate Dominium-local Git, changelog, context, review, ledger, and task
   reports.
6. Run validation and secret scan.
7. Write evidence and stop at `needs_review`.

## Validation Intent

Run AIDE Lite doctor, validate, test, selftest, eval, verify, review-pack,
ledger, commit, changelog, task, and Git workflow commands where available.
Do not run branch helper `--apply` or `--push`.

## Review Gate

Q33 completes only as `needs_review`; it does not approve product work,
doctrine rewrites, branch mutation, provider/model calls, or hook installation.
