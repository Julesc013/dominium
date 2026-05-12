# POST-CONVERGE-02 Root Wrapper / Tooling / Governance Cleanup

## Status

- Task ID: POST-CONVERGE-02
- Result: pass with review carryover
- Date/time: 2026-05-12T19:29:22+10:00
- Branch: `main`
- HEAD SHA: `49ee68ca8f69ee1606847719cc265f914bed455d`
- origin/main SHA: `49ee68ca8f69ee1606847719cc265f914bed455d`
- Local main sync: fast-forward clean; `git pull --ff-only origin main` reported already up to date.
- Working tree status before task: clean on `main...origin/main`.
- Working tree status after validation before commit: tracked POST-CONVERGE-02 changes only.

## Scope

This task targeted only:

- `__init__.py`
- `tool_ui_bind.cmd`
- `tool_ui_doc_annotate.cmd`
- `tool_ui_validate.cmd`
- `governance`
- `ide`
- `labs`
- `meta`
- `meta_extensions_engine.py`
- `numeric_discipline.py`
- `performance`
- `validation`

This task moved no product roots, runtime roots, domain roots, content/pack/profile roots, security/safety/spec/update roots, or core/control/net roots. It changed no source semantics, product IDs, executable names, install IDs, pack IDs, virtual-root IDs, support matrix status, build presets, UI behavior, ABI behavior, or feature logic.

## Pre-Cleanup State

| Path | Exists? | Tracked? | Referenced? | Classification | Notes |
| --- | --- | --- | --- | --- | --- |
| `__init__.py` | yes | yes | no direct repo imports found | retire_exception | Root package marker contained only a docstring. |
| `tool_ui_bind.cmd` | yes | yes | yes | compatibility_shim_required | Documented zero-setup wrapper through `scripts/dev/tool_shim.py`. |
| `tool_ui_doc_annotate.cmd` | yes | yes | yes | compatibility_shim_required | Documented zero-setup wrapper through `scripts/dev/tool_shim.py`. |
| `tool_ui_validate.cmd` | yes | yes | yes | compatibility_shim_required | Documented zero-setup wrapper through `scripts/dev/tool_shim.py`. |
| `governance` | yes | yes | yes | protected_governance_review | Active imports from release and tooling helpers; not doctrine authority. |
| `ide` | yes | yes | yes | generated_or_mirror_review | Root IDE projection boundary is referenced by quarantine/generation policy. |
| `labs` | yes | yes | yes | experimental_archive_move | Quarantined docs-only README; only live non-generated reference was archive manifest. |
| `meta` | yes | yes | yes | mixed_review | Active mixed semantic/provenance/tooling helper package. |
| `meta_extensions_engine.py` | yes | yes | yes | protected_governance_review | Active imports cross governance, compatibility, domain, distribution, and audit tooling. |
| `numeric_discipline.py` | yes | yes | yes | protected_governance_review | Active imports from domain truth/geometry/ephemeris code. |
| `performance` | yes | yes | yes | mixed_review | Active helper imports from domain performance logic. |
| `validation` | yes | yes | yes | mixed_review | Active unified validation engine imports from runtime, tools, shims, and tests. |

## Actions Taken

| Path | Action | New Location | Compatibility Shim? | Exception Status | Notes |
| --- | --- | --- | --- | --- | --- |
| `__init__.py` | removed_obsolete | none | no | retired_exception | No direct in-repo import dependency found. |
| `tool_ui_bind.cmd` | kept_compatibility_shim | root | yes | keep_exception_narrowed | Existing policy/docs/workflow references preserve the root shim. |
| `tool_ui_doc_annotate.cmd` | kept_compatibility_shim | root | yes | keep_exception_narrowed | Existing policy/docs/workflow references preserve the root shim. |
| `tool_ui_validate.cmd` | kept_compatibility_shim | root | yes | keep_exception_narrowed | Existing policy/docs/workflow references preserve the root shim. |
| `governance` | left_for_review | root | no | keep_exception_narrowed | Active release/tooling helper; AGENTS.md and canon remain authority. |
| `ide` | left_for_review | root | no | keep_exception_narrowed | Root remains generated IDE projection boundary. |
| `labs` | moved_to_archive | `archive/historical/labs/README.md` | no | retired_exception | Quarantined experiment README moved under archive ownership. |
| `meta` | left_for_review | root | no | keep_exception_narrowed | Protected mixed semantic ownership review remains required. |
| `meta_extensions_engine.py` | left_for_review | root | no | keep_exception_narrowed | Relocation would cross governance, compatibility, and domain imports. |
| `numeric_discipline.py` | left_for_review | root | no | keep_exception_narrowed | Relocation would touch numeric domain semantics. |
| `performance` | left_for_review | root | no | keep_exception_narrowed | Active domain performance helper imports remain. |
| `validation` | left_for_review | root | no | keep_exception_narrowed | Active runtime/tooling validation engine imports remain. |

## Reference Updates

- Updated `tests/contract/archive_manifest.json` so the labs entry points at `archive/historical/labs/README.md`.
- Updated `scripts/ci/check_repox_rules.py` so the archive-path guard allows `archive/historical/labs` instead of the retired root `labs`.
- Updated `contracts/repo/layout_exceptions.toml`, `docs/repo/LAYOUT_EXCEPTION_LEDGER.md`, `docs/repo/EXCEPTION_RETIREMENT_QUEUE.md`, `docs/repo/ROOT_INVENTORY.md`, `docs/repo/MOVE_MAP.md`, `docs/repo/ROOT_FILE_POLICY.md`, and `docs/repo/LAYOUT_ENFORCEMENT.md`.
- No workflow, build preset, runtime, product, UI, ABI, or support-matrix updates were needed.

## Exception Ledger Changes

| Exception ID | Path | Previous Active? | New Active? | New Status | Notes |
| --- | --- | --- | --- | --- | --- |
| `root_init_py` | `__init__.py` | yes | no | retired | Removed after reference review. |
| `governance_root` | `governance` | yes | yes | narrowed | Active governance profile helper; not canonical doctrine authority. |
| `ide_root` | `ide` | yes | yes | narrowed | Intentional IDE projection boundary remains. |
| `labs_root` | `labs` | yes | no | retired | Moved to `archive/historical/labs`. |
| `meta_root` | `meta` | yes | yes | narrowed | Mixed semantic/provenance/tooling surface remains protected review. |
| `meta_extensions_engine_file` | `meta_extensions_engine.py` | yes | yes | narrowed | Active cross-surface imports remain. |
| `numeric_discipline_file` | `numeric_discipline.py` | yes | yes | narrowed | Active numeric domain imports remain. |
| `performance_root` | `performance` | yes | yes | narrowed | Active domain performance helper imports remain. |
| `tool_ui_bind_cmd` | `tool_ui_bind.cmd` | yes | yes | narrowed | Root compatibility shim remains. |
| `tool_ui_doc_annotate_cmd` | `tool_ui_doc_annotate.cmd` | yes | yes | narrowed | Root compatibility shim remains. |
| `tool_ui_validate_cmd` | `tool_ui_validate.cmd` | yes | yes | narrowed | Root compatibility shim remains. |
| `validation_root` | `validation` | yes | yes | narrowed | Active unified validation engine remains protected review. |

## Remaining Wrapper / Tooling / Governance Exceptions

Still-active target exceptions:

- `tool_ui_bind.cmd`, `tool_ui_doc_annotate.cmd`, `tool_ui_validate.cmd`: documented developer compatibility shims.
- `governance`: active governance profile helper used by release/tooling; AGENTS.md and canon remain authority.
- `ide`: intentional generated IDE projection boundary.
- `meta`, `meta_extensions_engine.py`, `numeric_discipline.py`, `performance`, `validation`: active mixed or protected helper surfaces that require a later ownership review before relocation.

## Validation

Required validators:

- `python tools/validators/check_repo_layout.py --repo-root .`: pass; active exceptions 32; unexcepted violations 0.
- `python tools/validators/check_repo_layout.py --repo-root . --json`: pass; active exceptions 32; unexcepted violations 0.
- `python tools/validators/check_repo_layout.py --repo-root . --strict`: pass.
- `python tools/validators/check_root_allowlist.py --repo-root .`: pass; active exceptions 32; unexcepted violations 0.
- `python tools/validators/check_root_allowlist.py --repo-root . --json`: pass; active exceptions 32; unexcepted violations 0.
- `python tools/validators/check_root_allowlist.py --repo-root . --strict`: pass.
- `python tools/validators/check_distribution_layout.py --repo-root .`: pass; warnings 0.
- `python tools/validators/check_distribution_layout.py --repo-root . --strict`: pass.
- `python tools/validators/check_component_matrices.py --repo-root .`: pass; warnings 0.
- `python tools/validators/check_component_matrices.py --repo-root . --strict`: pass.

Supplemental checks:

- `python scripts/verify_docs_sanity.py --repo-root .`: pass.
- `python scripts/verify_build_target_boundaries.py --repo-root .`: pass.
- `python scripts/verify_ui_shell_purity.py --repo-root .`: pass.
- `python scripts/verify_abi_boundaries.py --repo-root .`: pass.
- JSON parse for `tests/contract/archive_manifest.json`, `tools/migration/root_inventory.json`, and `tools/migration/root_move_map.json`: pass.
- `python tests/contract/archive_presence_tests.py --repo-root .`: failed on pre-existing `legacy` and `tmp` manifest entries; the moved labs path was present. This was not part of the required POST-CONVERGE-02 validation set and was not remediated here.

AIDE preflight:

- `py -3 .aide/scripts/aide_lite.py doctor`, `validate`, and `pack`: not run because `py` is unavailable in this shell.
- `python .aide/scripts/aide_lite.py doctor`: pass with existing environment/status warnings.
- `python .aide/scripts/aide_lite.py validate`: pass with existing review-packet warnings.
- `python .aide/scripts/aide_lite.py pack --task "POST-CONVERGE-02 wrapper tooling governance cleanup"`: failed on the known Python 3.8 `Path.write_text(newline=...)` incompatibility also recorded by POST-CONVERGE-00.

Git checks:

- `git diff --check`: pass.
- `git diff --cached --check`: pass.

## Risks

- Root wrappers remain for compatibility and should not be copied for new commands.
- Governance, meta, numeric, performance, and validation material still need protected ownership review before relocation.
- No build, FAST, CMake, XStack, runtime proof, or playtest remediation was attempted.

## Next Recommended Task

`POST-CONVERGE-03 - Content / Pack / Profile / Bundle Cleanup`.
