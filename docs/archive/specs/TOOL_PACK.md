Status: HISTORICAL
Last Reviewed: 2026-02-01
Supersedes: none
Superseded By: docs/architecture/CANON_INDEX.md

This document is archived.
Reason: Superseded by docs/architecture/CANON_INDEX.md.
Do not use for implementation.

This document is archived.
Reason: Superseded by docs/architecture/CANON_INDEX.md.
Do not use for implementation.

This document is archived.
Reason: Superseded by unknown.
Do not use for implementation.

# ARCHIVED: dominium-tools pack

Archived: legacy pack workflow.
Reason: References deprecated pack layout and `manifest.txt` format.
Superseded by:
- `docs/specs/launcher/PACK_SYSTEM.md`
- `docs/specs/launcher/SPEC_LAUNCHER_PACKS.md`
- `docs/specs/SPEC_PACKAGES.md`
Still useful: historical context for early tooling expectations.

# dominium-tools pack

Pack/version builder.

Usage:
```
dominium-tools pack --version <ver> --output <versions_dir> [--include base,space,war]
```

- Reads existing packs under `data/packs/`.
- Produces `data/versions/<ver>/manifest.txt` listing included packs and basic metadata.
- Uses `dsys_*` I/O; ensure the destination directory exists.