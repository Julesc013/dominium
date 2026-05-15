# Install AIDE Lite Pack v0

## Command Import

From the source AIDE repository:

```text
py -3 .aide/scripts/aide_lite.py import-pack --pack .aide/export/aide-lite-pack-v0 --target <target-repo> --dry-run
py -3 .aide/scripts/aide_lite.py import-pack --pack .aide/export/aide-lite-pack-v0 --target <target-repo> --mode safe
```

`--mode safe` is the default. It skips optional broad roots such as `core/` and
non-reference `docs/` content and prints the exact planned writes plus skipped
paths during dry-run. Portable `docs/reference/` governance docs are safe-mode
files. Use `--mode full` only in reviewed local fixtures where copying optional
roots has been explicitly accepted.

## Manual Import

Copy only the safe portable subset from `files/` into the target repository:
`.aide/`, `.aide.local.example/`, `docs/reference/` governance docs,
`AGENTS.md.template`, and target templates. Do not manually copy optional
`core/` or broad non-reference `docs/` roots into a product repo unless that
target task explicitly authorizes them. Then fill the target templates under
`.aide/` with target-specific facts.

After import, run in the target repository:

```text
py -3 .aide/scripts/aide_lite.py doctor
py -3 .aide/scripts/aide_lite.py snapshot
py -3 .aide/scripts/aide_lite.py index
py -3 .aide/scripts/aide_lite.py repo inventory
py -3 .aide/scripts/aide_lite.py repo validate
py -3 .aide/scripts/aide_lite.py repo status
py -3 .aide/scripts/aide_lite.py quality ledger
py -3 .aide/scripts/aide_lite.py quality validate
py -3 .aide/scripts/aide_lite.py refactor status
py -3 .aide/scripts/aide_lite.py refactor plan
py -3 .aide/scripts/aide_lite.py refactor validate
py -3 .aide/scripts/aide_lite.py pack --task "<target next task>"
py -3 .aide/scripts/aide_lite.py adapter render
py -3 .aide/scripts/aide_lite.py adapter validate
py -3 .aide/scripts/aide_lite.py commit template
py -3 .aide/scripts/aide_lite.py git policy
py -3 .aide/scripts/aide_lite.py git plan
py -3 .aide/scripts/aide_lite.py github validate
```

Do not copy source `.aide/queue/`, generated context, reports, `.aide.local/`,
provider credentials, raw prompts, or raw responses. Generate adapter outputs
locally in the target repo after target-specific memory and context exist.
Commit hooks are copied as `.aide/hooks/commit-msg` but are not installed into
`.git/hooks`; hook installation remains an explicit target action.
