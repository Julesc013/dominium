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
check_directory_naming.py
check_file_naming.py
```

Default mode is audit mode. It exits zero and classifies current debt so the repo can record existing conflicts without weakening any existing validator.

`--strict` is available. In NAME-00 it fails only for blocker-class findings in validators that define blockers. Directory and file naming are warning-only until a later reviewed enforcement task decides which existing debts become hard failures.

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
