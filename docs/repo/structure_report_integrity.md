Status: DERIVED
Last Reviewed: 2026-05-22
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
- `files[]` with `path`, `size`, and `sha256`

For canonical structure work, `source_mode` must be `git_tracked` unless the
task explicitly authorizes a broader filesystem scan.

## Integrity Rules

- The manifest commit and branch must describe the evidence source.
- Bundle file hashes must match the manifest.
- Mixed-run artifacts are invalid.
- Generated and local roots such as `.aide.local/`, `.dominium.local/`,
  `build/`, `out/`, `dist/`, `artifacts/`, `reports/`, `tmp/`, and
  `__pycache__/` must be excluded from tracked-only source reports.
- A zip, when present, must contain only files listed by the manifest.

## Current Validator

Use:

```text
py -3 tools/validators/repo/check_structure_report_integrity.py --manifest <bundle>/manifest.json --strict
```

Without `--manifest`, the validator checks for known active tracked dirfiles
artifacts and reports whether they need an integrity manifest.

## Evidence Location

Task-local structure evidence should be written under ignored local roots such
as `.dominium.local/<task-id>/`. Commit only audits, policies, contracts, or
source validators unless a task explicitly requires retained generated evidence.
