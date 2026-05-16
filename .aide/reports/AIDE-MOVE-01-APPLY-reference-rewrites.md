# AIDE-MOVE-01-APPLY Reference Rewrites

## Summary

- Planned apply-phase rewrites: 6
- Applied rewrites: 6
- Extra rewrites applied: 0

## Applied

| File | Planned current reference | Applied replacement |
| --- | --- | --- |
| `.gitignore` | `!/ide/README.md` | Removed line. |
| `scripts/verify_docs_sanity.py` | `ide/README.md` | `docs/architecture/IDE_PROJECTIONS.md` |
| `docs/architecture/REPO_OWNERSHIP_AND_PROJECTIONS.md` | `/ide/README.md` | `/docs/architecture/IDE_PROJECTIONS.md` |
| `docs/architecture/IDE_PROJECTIONS.md` | `# IDE Projections (/ide)` | `# IDE Projections` |
| `docs/architecture/IDE_PROJECTIONS.md` | `/ide/README.md` | `/docs/architecture/IDE_PROJECTIONS.md` |
| `tools/aide/select_move_wave.py` | `ide/README.md and ide/manifests projection docs/examples` | `docs/architecture/IDE_PROJECTIONS.md only; keep ide/manifests deferred` |

## Preserved

- Historical references in root-recycling reports and audit evidence were preserved.
- Generated architecture registry and graph references remain review/regeneration items.
- No `ide/manifests/**` references were rewritten.
