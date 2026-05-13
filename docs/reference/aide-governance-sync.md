# AIDE Governance Sync

Dominium uses the local `.aide/` import for compact task packets, evidence,
commit discipline, WorkUnit recovery, and report-only Git workflow guidance.

Q33 refreshed portable governance from the canonical AIDE Lite Pack:

- `.aide/policies/commit-messages.yaml`
- `.aide/policies/task-resumption.yaml`
- `.aide/policies/work-units.yaml`
- `.aide/policies/recovery.yaml`
- `.aide/policies/git-workflow.yaml`
- `.aide/policies/branch-roles.yaml`
- `.aide/policies/promotion-rules.yaml`
- `.aide/policies/sync-policy.yaml`
- `.aide/policies/prune-policy.yaml`
- `.aide/git/helper-policy.yaml`
- `.aide/hooks/commit-msg`
- `.aide/git/commit-template.md`

The hook template is committed under `.aide/hooks/commit-msg` but is not
installed into `.git/hooks` automatically.

Run local checks with:

```powershell
py -3 .aide/scripts/aide_lite.py commit check --latest
py -3 .aide/scripts/aide_lite.py changelog preview
py -3 .aide/scripts/aide_lite.py task inspect
py -3 .aide/scripts/aide_lite.py git detect
py -3 .aide/scripts/aide_lite.py git plan
```

Git helper commands are dry-run by default. Do not run branch helper `--apply`
or `--push` without a reviewed queue item and explicit operator approval.

Dominium doctrine remains authoritative in repo-local doctrine files. AIDE
memory and packets should reference doctrine paths such as
`.aide/context/dominium-doctrine-refs.md`, `docs/canon/constitution_v1.md`,
`docs/canon/glossary_v1.md`, and `docs/planning/AUTHORITY_ORDER.md` rather
than copying doctrine text into `.aide/memory/`.
