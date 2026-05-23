Status: DERIVED
Last Reviewed: 2026-05-23
Supersedes: none
Superseded By: none
Stability: provisional
Scope: remaining repo-structure residuals after canonical structure finalization

# Structure Residual Classification

## Purpose

This document classifies residual structure warnings that are not safe to fix by
blind directory moves. It prevents stale report bundles or generic tree reviews
from treating classified residuals as proof that the top-level structure failed.

The current rule is:

- hard authority violations are blockers;
- ambiguous ownership and taxonomy items are warnings with focused follow-up
  tasks;
- broad source moves require a task that owns the affected taxonomy.

## Report Bundle Integrity

Tracked structure evidence must be produced in `git_tracked` mode with a single
manifest, shared run metadata, and verified hashes. Local generated bundles
belong under ignored roots such as `.dominium.local/<task-id>/`.

Use:

```text
py -3 tools/validators/repo/check_structure_report_integrity.py --repo-root . --write-bundle .dominium.local/<task-id> --strict
```

## Pack Authority

`contracts/package/packs/` is contract-only. It may contain direct Markdown
notes such as `README.md`; it must not contain authored pack IDs, pack payloads,
pack-local manifests, or generated package evidence.

Authored pack payloads live under `content/packs/`. Pack fixtures belong under
`tests/fixtures/package/` or an established test fixture route.

Pack-local `content/` directories under `content/packs/**` are classified as
legacy pack payload layout, not contract authority. They remain warnings until
`PACK-INTERNAL-LAYOUT-CANON-01` decides whether `content/` is a required pack
payload root or should normalize to `data/assets/docs/ui/scenarios`.

## Runtime And Engine Residuals

The following paths are classified residuals, not permission to create broad
bucket directories:

- `engine/compatx`: CompatX core policy and validator implementation.
- `runtime/compatx`: runtime-facing CompatX adapter/validator surface.
- `engine/foundation`: deterministic substrate pending boundary review; not a
  generic `core/common` replacement.
- `engine/serialization`: deterministic engine serialization only.
- `runtime/serialization`: runtime canonical JSON utilities; not
  `contracts/protocol`, save, replay, or package authority.
- `engine/session`: engine-side session common code pending boundary review.
- `runtime/session`: runtime session protocol/common surface.
- `runtime/project_graph`: accepted runtime service for the contract-backed
  project graph model.
- `runtime/ui/client`: accepted reusable client UI-facing systems per
  `APPS_THIN_01`.
- `runtime/ui/control/dui` and `runtime/include/dui`: accepted Dominium UI
  facade/control surfaces per `SPEC_DUI` and `STRUCTURE_CANON_SWEEP_01`.

Focused follow-up: `RUNTIME-RESIDUAL-TAXONOMY-01`.

Missing `runtime/projection/cli`, `runtime/projection/headless`, and
`runtime/projection/native` roots are classified as deferred projection-surface
work. Do not create empty placeholders for them without
`PROJECTION-CONFORMANCE-01` or equivalent scope.

## Workbench Residual

`apps/workbench/module/` and `apps/workbench/workspace/` are present.
`apps/workbench/shell/` is deferred until actual Workbench shell ownership
exists. Do not create an empty shell root just to silence a structural warning.

Focused follow-up: `WORKBENCH-SHELL-STRUCTURE-01`.

## Schema Residuals

`contracts/schema/` remains broad. The `engine` and `meta` buckets were routed
to `contracts/schema/runtime/engine/` and `contracts/schema/repo/meta/`.
Remaining first-level schema families still require classification before more
moves.

Focused follow-up: `SCHEMA-CANON-RESIDUAL-02`.

## Diagnostics Naming

The canonical contract root is singular:

```text
contracts/diagnostic/
```

`contracts/diagnostics/` is retired.

## AIDE State-Like Roots

Tracked `.aide/` roots such as `cache`, `queue`, `reports`, `ledgers`,
`release`, `models`, `providers`, and `tools` are classified as AIDE
control-plane, fixture, policy, or evidence roots. Mutable local state remains
out of tracked `.aide/` and belongs under `.aide.local/` or another ignored
local root.

Focused follow-up: `AIDE-STATE-CLASSIFICATION-01`.

## Tests Residuals

The tests tree is acceptable for governed development with warnings. Roots
outside the final proof taxonomy are not release blockers by themselves, but
they should not be used as precedent for new broad buckets.

## Validator

Use:

```text
py -3 tools/validators/repo/check_structure_residuals.py --repo-root . --strict
```

`--strict` fails on hard authority violations. `--strict-final` also fails on
classified warnings and is reserved for a later final-structure gate.
