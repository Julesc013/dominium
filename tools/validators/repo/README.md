Status: DERIVED
Last Reviewed: 2026-05-18
Supersedes: none
Superseded By: none
Stability: provisional
Task: NAME-00

# Repo Naming Validators

These validators implement the NAME-00 naming canon as non-destructive audit tools.

They inspect tracked paths only. They do not move, delete, rename, rewrite, generate build outputs, create shims, or retire exceptions.

## Validators

```text
check_no_src_source_dirs.py
check_path_terms.py
check_app_thinness.py
check_workbench_module_names.py
check_tools_taxonomy.py
check_directory_naming.py
check_file_naming.py
check_canonical_structure.py
check_provider_structure.py
check_schema_taxonomy.py
check_structure_report_integrity.py
check_structure_residuals.py
```

Default mode is audit mode. It exits zero and classifies current debt so the repo can record existing conflicts without weakening any existing validator.

`--strict` is available. In NAME-00 it fails only for blocker-class findings in validators that define blockers. Directory and file naming are warning-only until a later reviewed enforcement task decides which existing debts become hard failures.

`check_workbench_module_names.py` protects `apps/workbench/module/` as a
presentation-module namespace. Reusable behavior belongs under the owning
runtime, game, tool, app, or contract root rather than inside Workbench UI
folders.

`check_tools_taxonomy.py` is the TOOLS-FOLD-01 enforcement surface. It fails in
strict mode when active tracked files recreate broad first-level `tools/` roots
such as `tools/validator`, `tools/gui`, `tools/render`, `tools/world_editor`, or
other source/product/runtime/domain mirrors. It inspects tracked paths and ignores
untracked, generated, and archive material by default.

`check_canonical_structure.py` is the CANON-STRUCTURE-FINALIZE-NOW-01 hard
blocker surface. It fails strict mode for retired active roots and clear old
paths such as `game/rules`, retired runtime names, old test buckets, and tracked
generated/local roots. Remaining taxonomy debt is reported as warnings unless
`--strict-final` is used.

It also blocks top-level `modules/`, `plugins/`, `services/`, and `workspaces/`
roots. Module declarations belong in `contracts/module/` or pack manifests;
module payloads belong in `content/packs/`; module implementations belong under
their actual ownership root.

`check_provider_structure.py` is the PROVIDER-STRUCTURE-CANON-01 guardrail. It
enforces service-first provider paths, blocks vendor-shaped roots such as
`runtime/raylib` or app-specific provider variants, validates release provider
profiles, and checks for third-party include leakage outside provider/external
boundaries.

`check_schema_taxonomy.py` blocks the retired `contracts/schema` buckets and
flat schema filename prefixes that were routed to domain/runtime/game/repo
taxonomy roots during canonical structure cleanup.

Provider and third-party validators also expose focused entrypoints:

```text
tools/validators/third_party/check_vendor_manifest.py
tools/validators/third_party/check_forbidden_includes.py
tools/validators/provider/check_provider_manifest.py
tools/validators/provider/check_provider_conformance.py
```

Those entrypoints are thin policy gates over the same provider, profile,
third-party manifest, forbidden include, and conformance rules.

`check_structure_report_integrity.py` verifies task-local tracked-only structure
bundle manifests, can write a fresh local tracked-only structure bundle, and
reports active tracked dirfiles artifacts that lack an explicit integrity
manifest.

`check_structure_residuals.py` classifies remaining schema, pack, runtime, AIDE,
and tests taxonomy residuals without performing source-tree moves. It fails
strict mode only for mechanically knowable authority violations.

## Example

```powershell
py -3 tools/validators/repo/check_path_terms.py --repo-root . --out .aide/reports/NAME-00-path-conflicts.json --md-out .aide/reports/NAME-00-path-conflicts.md
```

## Relationship To Layout Validators

These validators do not replace:

```text
tools/validators/check_repo_layout.py
tools/validators/check_root_allowlist.py
tools/validators/check_distribution_layout.py
tools/validators/check_component_matrices.py
```

The existing strict validators remain the source-layout gate. NAME-00 adds naming-law evidence and future enforcement surfaces.
