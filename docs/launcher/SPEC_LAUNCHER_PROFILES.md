--------------------------------
OWNERSHIP & RESPONSIBILITY
--------------------------------
ENGINE:
- None. This spec is implemented under `launcher/`.

GAME:
- None. This spec is implemented under `launcher/`.

TOOLS:
- None. Tools may only consume public APIs if needed.

SCHEMA:
- None (no canonical schema formats defined here).

FORBIDDEN:
- No launcher/setup orchestration logic in engine or game.
- No engine internal headers exposed outside engine targets.
- No game rules or policy implemented inside engine primitives.

DEPENDENCIES:
- Engine -> libs/ and schema/ only (never game/launcher/setup/tools).
- Game -> engine public API and schema/ only.
- Tools -> engine public API, game public API, and schema/ only.
- Launcher/Setup (if applicable) -> libs/contracts + schema (launcher may also use engine public API).
--------------------------------
# SPEC_LAUNCHER_PROFILES — Runtime Selection Profiles (Authoritative)

This spec defines launcher-driven runtime selection profiles: how users request
compatibility/performance modes, how backends are preferred/overridden, and how
determinism requirements are enforced.

Primary ABI surface:
- `include/domino/profile.h`
- `include/domino/caps.h`

## 1. Profile object (C ABI)

The launcher produces a `dom_profile` POD:
- `kind`: `DOM_PROFILE_COMPAT`, `DOM_PROFILE_BASELINE`, `DOM_PROFILE_PERF`
- `lockstep_strict`: 0/1
- backend preferences:
  - `preferred_gfx_backend` (string)
  - `overrides[]` list of `(subsystem_key, backend_name)` pairs

No STL or dynamic allocation crosses this boundary.

## 2. CLI flags

Both `dominium_game` and `dominium-launcher` accept:
- `--profile=compat|baseline|perf`
- `--lockstep-strict=0|1`
- `--gfx=<backend>` (e.g. `soft`, `dx11`, `null`)
- `--sys.<facet>=<backend>` (examples: `--sys.fs=win32`, `--sys.net=stub`)
- `--print-caps`
- `--print-selection`

The runtime explicitly rejects language-standard selection flags at runtime
(e.g. `--cstd`, `--cppstd`), as these are build/toolchain concerns.

## 3. Selection behavior (high level)

When `--print-selection` is used, the runtime:
1. registers compiled backends into the central registry
2. finalizes the registry deterministically
3. selects backends using the provided `dom_profile`
4. prints:
   - available backends per subsystem
   - selected backend per subsystem
   - determinism grade and selection reason

Profile kind affects which perf class is preferred (see
`docs/SPEC_CAPABILITY_REGISTRY.md`).

## 4. Lockstep strict behavior

When `--lockstep-strict=1`, selection enforces determinism grades:
- lockstep-relevant subsystems must select `D0`
- selection fails explicitly if no eligible `D0` backend exists

Non-lockstep subsystems (renderer/audio) may remain `D2` as long as they cannot
influence authoritative simulation outcomes.

## 5. Example commands

Inspect available backends and selection:
```
dominium_game.exe --profile=compat --lockstep-strict=1 --print-selection
dominium_game.exe --gfx=null --print-selection
```

