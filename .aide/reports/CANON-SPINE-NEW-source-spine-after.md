# CANON-SPINE-NEW Source Spine After

The active source spine now follows these ownership planes:

- `apps/`: thin product entrypoints plus `apps/workbench/` user-facing modules.
- `engine/`: deterministic substrate.
- `game/`: rule/world/domain meaning.
- `runtime/`: shell, platform, render, UI, input, audio, network, storage, package, profile, save, replay, update, and capability services.
- `contracts/`: machine-readable law with singular category roots.
- `content/`: authored data and assets with `content/domains/` as the domain data collection.
- `tools/`: non-interactive repo/build/codegen/package/release/migration/validation tooling.
- `tests/`: proof and regression.
- `docs/`: human explanation and audit evidence.
- `archive/`: historical/generated/quarantine retention.

Root-level generated/local roots remain untracked only.
