Status: DERIVED
Stability: provisional
Future Series: DOC-CONVERGENCE
Replacement Target: Canon-aligned documentation set tracked by REPO-REVIEW-3.

# Repo Review 3 Final

Source: `tools/review/tool_doc_inventory.py`

## Alignment Status Counts

- `aligned`: `842`
- `contradictory`: `2`
- `legacy_reference_only`: `799`
- `partially_aligned`: `292`
- `superseded`: `47`

## Top Contradictions

- `duplicate glossary surfaces exist; only the canon glossary v1 is binding.` [`docs/GLOSSARY.md`, `docs/canon/glossary_v1.md`]
- `UI mode selection rules diverge between the older app doc and the frozen AppShell order.` [`docs/app/UI_MODES.md`, `docs/appshell/APPSHELL_CONSTITUTION.md`, `docs/release/FROZEN_INVARIANTS_v0_0_0.md`]
- `layout docs still describe top-level product directories that no longer match the actual repository tree.` [`docs/architecture/DIRECTORY_STRUCTURE.md`, `docs/architecture/ARCH_REPO_LAYOUT.md`, `docs/audit/REPO_TREE_INDEX.md`]

## Top Missing Docs

- `high` `virtual paths` -> `docs/lib/VIRTUAL_PATH_LAYER.md`
- `high` `standalone product guarantees` -> `docs/release/STANDALONE_PRODUCT_GUARANTEES.md`
- `medium` `platform matrix` -> `docs/release/PLATFORM_MATRIX.md`
- `medium` `validation unification` -> `docs/validation/VALIDATION_UNIFICATION.md`
- `medium` `user-facing UI mode selection` -> `docs/app/UI_MODE_SELECTION.md`

## Readiness

- Entrypoint unification: ready with doc supersession map in place.
- Validation unification: partially ready; canonical gap remains tracked in `docs/audit/DOC_GAPS.md`.
