# MOVE-FAMILY-00B-APPLY Reference Rewrites

## Result

PASS_WITH_WARNINGS.

## Applied Rewrite Groups

| File | Rewrite |
| --- | --- |
| `.gitignore` | Removed the `ide/manifests/**` tracked-source unignore rules while preserving `/ide/**` as ignored generated output. |
| `scripts/verify_docs_sanity.py` | Updated required schema path to `contracts/projections/ide/projection_manifest.schema.json` and allowed `contracts/projections/**` doc targets. |
| `docs/architecture/REPO_OWNERSHIP_AND_PROJECTIONS.md` | Updated authoritative metadata owner from `/ide/manifests/**` to `/contracts/projections/ide/**`. |
| `docs/architecture/PROJECTION_LIFECYCLE.md` | Updated the schema path to `/contracts/projections/ide/projection_manifest.schema.json`. |
| `docs/architecture/IDE_PROJECTIONS.md` | Split source schema/examples under `/contracts/projections/ide/**` from generated manifests under `/ide/manifests/`. |

## Preserved References

Generated-output references remain in:

- `scripts/ide_gen.sh`
- `scripts/ide_gen.bat`
- `cmake/ide/IdeProjectionManifest.cmake`
- `data/release/preset_and_toolchain_registry.json`
- generated-output notes in docs.

Historical/planning/audit references remain in prior root-recycling docs, audit reports, data planning mirrors, and generated architecture evidence. These were not rewritten because the MOVE-FAMILY-00B plan marked them as historical, generated, later, or review-only.

## Blockers

None.
