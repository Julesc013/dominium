Status: DERIVED
Last Reviewed: 2026-05-23
Supersedes: none
Superseded By: none
Stability: provisional
Scope: repo structure evidence, tracked-only exports, and generated dirfile bundles

# Structure Report Integrity

## Purpose

Structure reports are evidence, not source truth. A report bundle may be used for
canonical routing work only when it is internally consistent with its manifest
and clearly states the source mode that produced it.

## Required Manifest Fields

A structure report bundle must include a manifest with:

- `schema_version`
- `source_mode`
- `commit`
- `branch`
- `dirty`
- `generated_utc`
- `run_id`
- `files[]` with `path`, `size`, and `sha256`

For canonical structure work, `source_mode` must be `git_tracked` unless the
task explicitly authorizes a broader filesystem scan.

## Integrity Rules

- The manifest commit and branch must describe the evidence source.
- `dir_tree.json`, `dir_tree.txt`, and `dirfiles_run.log` must repeat the
  same `source_mode`, `commit`, `branch`, `dirty`, `generated_utc`, and
  `run_id` values when they are present in the bundle.
- Bundle file hashes must match the manifest.
- Mixed-run artifacts are invalid.
- Generated and local roots such as `.aide.local/`, `.dominium.local/`,
  `build/`, `out/`, `dist/`, `artifacts/`, `reports/`, `tmp/`, and
  `__pycache__/` must be excluded from tracked-only source reports.
- A zip, when present, must contain only files listed by the manifest, and its
  report members must match the manifest hashes.
- The manifest is the external authority for the bundle and is not required to
  hash itself.

## Current Validator

Use:

```text
py -3 tools/validators/repo/check_structure_report_integrity.py --manifest <bundle>/dirfiles_manifest.json --strict
```

To produce a fresh local tracked-only bundle:

```text
py -3 tools/validators/repo/check_structure_report_integrity.py --repo-root . --write-bundle .dominium.local/<task-id> --strict
```

Without `--manifest`, the validator checks for known active tracked dirfiles
artifacts and reports whether they need an integrity manifest.

## Evidence Location

Task-local structure evidence should be written under ignored local roots such
as `.dominium.local/<task-id>/`. Commit only audits, policies, contracts, or
source validators unless a task explicitly requires retained generated evidence.
