# AIDE Lite Pack v0

Pack id: `aide-lite-pack-v0`

This is a portable metadata and tooling pack for target repositories. It is
generated from AIDE's repo-local no-call token-survival foundation. Q31 exports
portable Q27-Q35 governance: structured commit discipline, changelog preview,
task/WorkUnit recovery, generic Git workflow policy, dry-run Git helper support,
and report-only GitHub/CI advisory policy. Q36 adds prompt normalization, Q37
adds repo intelligence policies, schemas, docs, tests, and commands, Q38 adds
advisory file-quality ledger support, and Q39 adds dry-run refactor control
schemas and commands. Q24 adapter templates remain
included so target repositories can generate local guidance previews for
existing tools after import.

The pack intentionally excludes AIDE's source profile, queue history, project
memory, generated context, reports, route/cache/controller/latest status,
provider/Gateway status reports, eval runs, source-generated repo intelligence
indexes, source-generated quality reports, source-generated refactor plans,
`.aide.local/`, raw prompts, raw responses, and secrets.

Q25 makes command import default to `--mode safe`, which plans and writes only
portable `.aide/`, `.aide.local.example/`, target templates, portable
`docs/reference/` governance docs, `AGENTS.md`, and `.gitignore` local-state
rules. Optional broad roots such as `core/` and non-reference `docs/` content
remain in the pack for reviewed fixtures but are skipped unless `--mode full`
is selected explicitly.

Use `install.md` for manual and command-based import steps.
