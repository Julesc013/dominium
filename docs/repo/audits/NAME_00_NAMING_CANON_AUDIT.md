Status: DERIVED
Last Reviewed: 2026-05-18
Supersedes: none
Superseded By: none
Stability: provisional
Task: NAME-00

# NAME-00 Naming Canon Audit

## Result

Status: PASS with transitional warnings.

NAME-00 adds naming law only. It does not move files, delete files, rename files, rewrite imports, rewrite references, create shims, apply move maps, apply salvage maps, retire exceptions, mutate runtime behavior, mutate content identity, or alter semantic contract IDs.

## Authority Read

Current naming and layout authority is derived from:

- `docs/canon/constitution_v1.md`
- `docs/canon/glossary_v1.md`
- `AGENTS.md`
- `contracts/repo/layout.contract.toml`
- `contracts/repo/root_allowlist.toml`
- `contracts/repo/layout_exceptions.toml`
- `contracts/distribution/layout.contract.toml`
- `contracts/release/component_matrix.contract.toml`
- `docs/repo/REPO_LAYOUT_TARGET.md`
- `docs/repo/OWNERSHIP_RULES.md`
- `docs/repo/DOMAIN_SPLIT_RULES.md`
- `docs/repo/DISTRIBUTION_LAYOUT_CANON.md`
- `docs/release/COMPONENT_MATRIX.md`
- `docs/repo/root-recycling/ROOT_RECYCLING_RUNBOOK.md`
- `docs/repo/root-recycling/MOVE_BULK_BATCH_SEQUENCE.md`

`docs/restructure/FUTURE_LAYOUT_PROPOSAL.md` is retained as historical planning input. Its `/src` proposal is explicitly superseded by the post-CONVERGE source-root model.

## Deliverables

- `contracts/repo/naming.contract.toml`
- `contracts/repo/naming.schema.json`
- `docs/repo/directory_naming.md`
- `docs/repo/file_naming.md`
- `docs/repo/no_src_source_policy.md`
- `docs/repo/module_layout.md`
- `docs/repo/language_ownership.md`
- `tools/validators/repo/check_no_src_source_dirs.py`
- `tools/validators/repo/check_path_terms.py`
- `tools/validators/repo/check_directory_naming.py`
- `tools/validators/repo/check_file_naming.py`
- `tools/validators/repo/README.md`
- `.aide/reports/NAME-00-*`

## Current Conflict Classification

The known current conflict classes are:

- historical `src`, `source`, and `legacy` pockets under `archive/`;
- transitional `packs/source/**` identity debt under an active bad-root exception;
- active top-level bad roots still excepted by `contracts/repo/layout_exceptions.toml`;
- planned internal rename targets such as `runtime/appshell`, `game/domains`, and `contracts/schemas`;
- Python placement under roots whose final language law is stricter than current implementation state.

These are not immediate NAME-00 blockers because this task is no-apply and the conflicts already existed under layout exceptions or historical archive classification.

## Future MOVE-BULK Effect

Future MOVE-BULK B-G refinement must consume `contracts/repo/naming.contract.toml` before selecting targets.

If a path can safely move, the target must use ownership nouns and the singular/plural grammar. If a path has unclear identity, ABI, runtime, policy, release, or language meaning, it remains deferred.

## Contract And Schema Impact

New contract surface: `dominium.repo.naming.v1`.

No existing semantic contract IDs were changed.
