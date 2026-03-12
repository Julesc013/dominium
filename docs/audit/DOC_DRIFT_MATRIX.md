Status: DERIVED
Stability: provisional
Future Series: DOC-CONVERGENCE
Replacement Target: Canon-aligned documentation set tracked by REPO-REVIEW-3.

# Doc Drift Matrix

Source: `tools/review/tool_doc_inventory.py`

## Conflicting Definitions And Duplicate Specs

- `high` `duplicate_spec`: duplicate glossary surfaces exist; only the canon glossary v1 is binding. [`docs/GLOSSARY.md`, `docs/canon/glossary_v1.md`]
- `high` `conflicting_definition`: UI mode selection rules diverge between the older app doc and the frozen AppShell order. [`docs/app/UI_MODES.md`, `docs/appshell/APPSHELL_CONSTITUTION.md`, `docs/release/FROZEN_INVARIANTS_v0_0_0.md`]
- `high` `conflicting_definition`: layout docs still describe top-level product directories that no longer match the actual repository tree. [`docs/architecture/DIRECTORY_STRUCTURE.md`, `docs/architecture/ARCH_REPO_LAYOUT.md`, `docs/audit/REPO_TREE_INDEX.md`]
- `medium` `duplicate_spec`: root architecture summary overlaps with binding constitutional docs and can drift if treated as equivalent authority. [`docs/ARCHITECTURE.md`, `docs/architecture/ARCH0_CONSTITUTION.md`, `docs/canon/constitution_v1.md`]
- `medium` `duplicate_spec`: XStack governance is documented both as a narrative overview and as a generated current-state validation surface map. [`docs/XSTACK.md`, `docs/audit/VALIDATION_STACK_MAP.md`]

## Missing Docs Required For v0.0.0

- `high` `virtual paths` -> `docs/lib/VIRTUAL_PATH_LAYER.md`: REPO-REVIEW-2 found wide direct-path usage and there is no single current doctrine for the virtual path layer.
- `high` `standalone product guarantees` -> `docs/release/STANDALONE_PRODUCT_GUARANTEES.md`: setup guarantees exist, but there is no single current release doc for client/server/launcher/setup standalone guarantees.
- `medium` `platform matrix` -> `docs/release/PLATFORM_MATRIX.md`: cross-platform gate outputs exist, but there is no stable release-facing platform support matrix.
- `medium` `validation unification` -> `docs/validation/VALIDATION_UNIFICATION.md`: RepoX, AuditX, TestX, CompatX, and ARCH-AUDIT surfaces are documented in fragments rather than one convergence doc.
- `medium` `user-facing UI mode selection` -> `docs/app/UI_MODE_SELECTION.md`: the old UI mode summary is contradictory and the current mode order only appears indirectly in AppShell and release-freeze docs.
