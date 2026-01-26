# Content and Storage Model (STOR0)

Status: binding.
Scope: runtime data layout, storage safety, and path rules.

## Canonical runtime layout
Runtime data MUST live under a single root with this layout:
```
data/
  packs/
  saves/
  replays/
  modpacks/
  workspaces/
  cache/
    assets/
    derived/
  index/
  logs/
  profiles/
```

## Rules (hard)
- No other runtime data paths are allowed.
- No raw file paths are stored inside saves, packs, or WorldDefinitions.
- Cache is disposable and never required for correctness.
- Logs are non-authoritative and never inputs to simulation.
- Saves and replays are deterministic, extension-preserving artifacts.
- Data root must be relocatable (CLI `--data-root`).

## Storage boundaries
- Packs are immutable inputs (content + capability declarations).
- Saves and replays are outputs and must be self-describing.
- Cache may be wiped without affecting correctness.
- Any derived artifact must declare provenance.
- Indexes are optional caches only; deletion must not affect correctness.

## Path safety
- File paths are resolved by the runtime; data never embeds absolute or host paths.
- Paths are never used as identifiers.
- Paths are never used to resolve authority or capabilities.

## See also
- `docs/arch/DIRECTORY_CONTEXT.md`
- `docs/specs/SPEC_FS_CONTRACT.md`
- `docs/arch/WORLDDEFINITION.md`
