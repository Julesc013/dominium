Status: DERIVED
Stability: provisional
Future Series: DOC-CONVERGENCE
Replacement Target: Canon-aligned documentation set tracked by REPO-REVIEW-3.

# Doc Gaps

Source: `tools/review/tool_doc_inventory.py`

- `high` `virtual paths`: create `docs/lib/VIRTUAL_PATH_LAYER.md` because REPO-REVIEW-2 found wide direct-path usage and there is no single current doctrine for the virtual path layer.
- `high` `standalone product guarantees`: create `docs/release/STANDALONE_PRODUCT_GUARANTEES.md` because setup guarantees exist, but there is no single current release doc for client/server/launcher/setup standalone guarantees.
- `medium` `platform matrix`: create `docs/release/PLATFORM_MATRIX.md` because cross-platform gate outputs exist, but there is no stable release-facing platform support matrix.
- `medium` `validation unification`: create `docs/validation/VALIDATION_UNIFICATION.md` because RepoX, AuditX, TestX, CompatX, and ARCH-AUDIT surfaces are documented in fragments rather than one convergence doc.
- `medium` `user-facing UI mode selection`: create `docs/app/UI_MODE_SELECTION.md` because the old UI mode summary is contradictory and the current mode order only appears indirectly in AppShell and release-freeze docs.
