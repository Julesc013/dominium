# Headless Workflows (Setup CLI v1)

This document shows deterministic, non-interactive workflows using the `dominium-setup` CLI.

Notes:

- Use `--deterministic 1` (default) for byte-stable outputs in CI.
- Prefer JSON outputs and parse `status_code` (see `docs/setup/CLI_JSON_SCHEMAS.md`).

## Offline install (portable)

1) Validate the manifest:

`dominium-setup manifest validate --in <manifest.dsumanifest>`

2) Export invocation:

`dominium-setup export-invocation --manifest <manifest.dsumanifest> --op install --scope portable --components core --out <install.dsuinv>`

3) Resolve + preview:

`dominium-setup resolve --manifest <manifest.dsumanifest> --invocation <install.dsuinv>`

4) Produce a plan file:

`dominium-setup plan --manifest <manifest.dsumanifest> --invocation <install.dsuinv> --out <plan.dsuplan>`

5) Apply:

`dominium-setup apply --plan <plan.dsuplan>`

6) Verify:

`dominium-setup verify --state <installed_state.dsustate> --format json`

Exit code `2` indicates integrity issues (missing/modified/extra files).

## Server / headless install (system scope)

Use explicit scope and avoid prompts:

`dominium-setup export-invocation --manifest <manifest.dsumanifest> --op install --scope system --out <install.dsuinv>`

`dominium-setup plan --manifest <manifest.dsumanifest> --invocation <install.dsuinv> --out <plan.dsuplan>`

`dominium-setup apply --plan <plan.dsuplan>`

## CI verification gate

Run verify and treat exit code `2` as a failed gate:

`dominium-setup verify --state <installed_state.dsustate> --format json`

Suggested CI logic:

- `0`: pass
- `2`: fail (integrity issues)
- `3`: fail (invalid input)
- `1/4`: fail (fatal/unsupported)

## Repair workflow

1) Export invocation:

`dominium-setup export-invocation --manifest <manifest.dsumanifest> --op repair --out <repair.dsuinv>`

2) Resolve a repair plan (scope inferred from state when possible):

`dominium-setup resolve --manifest <manifest.dsumanifest> --state <installed_state.dsustate> --invocation <repair.dsuinv>`

3) Build a plan:

`dominium-setup plan --manifest <manifest.dsumanifest> --state <installed_state.dsustate> --invocation <repair.dsuinv> --out <repair.dsuplan>`

4) Dry-run the apply to preview txn impact:

`dominium-setup apply --plan <repair.dsuplan> --dry-run`

5) Apply for real:

`dominium-setup apply --plan <repair.dsuplan>`

## Rollback (journal replay)

If an apply fails or is interrupted, rollback can be driven from the journal path emitted by `apply`:

`dominium-setup rollback --journal <txn.dsujournal>`

For safe preview:

`dominium-setup rollback --journal <txn.dsujournal> --dry-run`

## Export logs

Export a binary `.dsulog` to JSON for ingestion:

`dominium-setup export-log --log <audit.dsu.log> --out <audit.json> --format json`

Or to deterministic TSV:

`dominium-setup export-log --log <audit.dsu.log> --out <audit.tsv> --format txt`
