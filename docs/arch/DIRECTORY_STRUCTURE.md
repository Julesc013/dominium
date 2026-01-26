# Directory Structure (FS0)

Status: binding.
Scope: locked directory structure for source tree and runtime data root.

## A) Source Tree (read-only at runtime)
```
repo/
├── engine/
├── game/
├── client/
├── server/
├── launcher/
├── setup/
├── tools/
├── schema/
├── docs/
├── tests/
├── ci/
├── cmake/
├── libs/
├── sdk/
└── legacy/        # quarantined, read-only
```

Rules:
- No runtime writes here.
- No packs, saves, mods, or caches here.
- No absolute paths referenced by code.

## B) Runtime Data Root (relocatable)
```
data/
├── packs/
├── saves/
├── replays/
├── modpacks/
├── workspaces/
├── cache/
│   ├── assets/
│   └── derived/
├── index/
├── logs/
└── profiles/
```

Rules:
- This is the ONLY mutable runtime root.
- Must be selectable via CLI/env (`--data-root`).
- Cache is disposable and never required for correctness.
- Indexes are optional caches only.
- Paths stored in data are relative to the data root, never absolute.

## See also
- `docs/arch/CONTENT_AND_STORAGE_MODEL.md`
- `docs/arch/DIRECTORY_CONTEXT.md`
