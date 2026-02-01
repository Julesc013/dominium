Status: DERIVED
Last Reviewed: 2026-02-01
Supersedes: none
Superseded By: none

# Build Dist Output Specification

This document defines the frozen, deterministic distribution layout used when
targets are routed into `dist/` via `dist_set_role`. Default build outputs
remain under the build directory; dist routing is opt-in.

Goals:
- one unified output root: `dist/`
- deterministic, media-ready, copy-safe layout (FAT/ISO/USB/zip)
- no build-system leakage in paths
- runtime payload separated from symbols

Validation is performed by `verify_dist` using `tools/validate_dist.cmake`.

## Frozen Directory Spec

```
dist/
  meta/
    dist.json
    targets.json
    files.json
    build.txt
    ver.txt
    hash.txt
    rules.txt

  docs/
    readme.txt
    licenses.txt
    notes.txt

  res/
    common/
    locale/
    packs/

  cfg/
    default/
    profiles/
    schemas/

  sys/
    winnt/
      x86/
      x64/
      arm64/
    win9x/
      x86/
    win16/
      x86/
    msdos/
      x86/
    os2/
      x86/
    macos/
      x64/
      arm64/
    macos9/
      ppc/
      m68k/
    macos8/
      ppc/
      m68k/
    macos7/
      m68k/
    linux/
      x86/
      x64/
      arm64/
    bsd/
      x64/
      arm64/
    android/
      arm64/
    ios/
      arm64/
    web/
      wasm/

  pkg/
    win/
    mac/
    linux/
    android/
    ios/
    web/

  redist/
    msvc/
    dx/
    other/

  sym/
    winnt/
    win9x/
    win16/
    msdos/
    os2/
    macos/
    macos9/
    macos8/
    macos7/
    linux/
    bsd/
    android/
    ios/
    web/
```

Note: only the active build leaf is populated under `sys/` and `sym/`.

## Leaf Layout Contract (Required for Every sys/<os>/<arch>/ Leaf)

```
sys/<os>/<arch>/
  bin/
    launch/
    game/
    engine/
    rend/
    tools/
    share/
  lib/
  etc/
  man/
```

Required files per leaf:
- `sys/<os>/<arch>/etc/leaf.json`
- `sys/<os>/<arch>/man/readme.txt`

## Runtime Seed (Minimal Install + Home Layout)

For rapid testing, CMake can seed a minimal install state and home layout under
the active leaf. This is additive to the frozen layout and keeps the core
artifact routing unchanged.
The `dist_seed` target is defined under `tools/dist_seed` and is not part of
the root build graph unless that subdirectory is added.

Seeded paths:
- `sys/<os>/<arch>/.dsu/installed_state.dsustate`
- `sys/<os>/<arch>/dominium_install.json`
- `sys/<os>/<arch>/repo/{products,packs,mods}`
- `sys/<os>/<arch>/{instances,artifacts,audit,exports,temp}`
Note: `.dsu` is a reserved seed directory (dot-prefix exception).

Seed target (when `dist_seed` is available; defined under `tools/dist_seed`):
```
cmake --build <builddir> --target dist_seed
```

Options:
- `-DDOM_DIST_SEED_RUNTIME=ON|OFF` (default: ON)
- `-DDOM_DIST_INSTALL_TYPE=portable|user|system` (default: portable)
- `-DDOM_DIST_BUILD_CHANNEL=dev|beta|stable` (default: dev)

Note: the seed uses deterministic placeholders (fixed install_id and timestamp)
to keep dist outputs stable. For real installs, use `dominium-setup` or the
packaging pipeline.

## Naming Contract (Frozen)

Directories:
- Allowed chars: `a-z0-9_`
- Lowercase only
- No spaces

Filenames:
- Allowed chars: `a-z0-9_.-`
- Lowercase only
- No spaces
- No leading `-`
- No trailing `.`
- No DOS device basenames: `con` `prn` `aux` `nul` `com1..com9` `lpt1..lpt9`
- No version numbers in filenames (versioning is metadata)

## Role-Based Binary Naming (Frozen; Extension Platform-Native)

These names are enforced by `tools/validate_dist.cmake` when `verify_dist` runs.

- launcher exe: `launch_dominium.<ext>`
- game exe: `game_dominium.<ext>`
- tools: `tool_<name>.<ext>`
- engine lib: `eng_domino.<ext>`
- shared core lib: `core_dominium.<ext>`
- renderer libs: `rend_<backend>.<ext>`

## Target naming

Dist routing does not rename targets. Output names are defined per target via
`OUTPUT_NAME` in component `CMakeLists.txt`; `dist_set_role` only changes the
output directory.

## CMake Dist Routing

The dist module computes the active leaf and can route final link outputs into
`dist/` for targets that call `dist_set_role`. Targets that do not call
`dist_set_role` continue to use the default build output directories.

Entry points:
- `cmake/dist_output.cmake`
- `dist_init(DIST_ROOT <path> [DIST_OS <token>] [DIST_ARCH <token>] [DIST_VARIANT <token>])`
- `dist_set_role(<target> <launch|game|engine|rend|tools|share>)`

Multi-config (MSVC):
- Output directories are set per-config but keep the same leaf path.
- Use `--config` for builds; do not rely on a `Debug/` or `Release/` folder.

Single-config (Ninja/MinGW):
- Output directories are set once based on `CMAKE_BUILD_TYPE`.

Symbols (MSVC PDB) go under `dist/sym/<os>/<arch>/...` mirroring the runtime
layout.

## Build Examples

MSVC x64 (Visual Studio generator):
```
cmake --preset msvc-release
cmake --build --preset msvc-release
cmake --build --preset msvc-release --target dist_meta
cmake --build --preset msvc-release --target verify_dist
```

MSYS2 MinGW x64 (Ninja):
```
cmake --preset msys2-release
cmake --build --preset msys2-release
cmake --build --preset msys2-release --target dist_meta
cmake --build --preset msys2-release --target verify_dist
```

## Variant Axis

To allow multiple toolchains side-by-side, set:
```
cmake -S . -B build/msvc -DDOM_DIST_VARIANT=msvc
cmake -S . -B build/mingw -DDOM_DIST_VARIANT=mingw
```

This produces:
```
dist/sys/<os>/<arch>/<variant>/
dist/sym/<os>/<arch>/<variant>/
```

Only enable a variant when you must keep toolchains in the same `dist/` root.

## Metadata Outputs

Generated by the `dist_meta` target:
- `dist/meta/dist.json` (schema + build info)
- `dist/meta/targets.json` (active build tuple)
- `dist/meta/files.json` (path + size + sha256)
- `dist/meta/hash.txt` (sha256 lines)
- `dist/meta/build.txt` (toolchain, generator, config)
- `dist/meta/ver.txt` (project version)
- `dist/meta/rules.txt` (layout/naming rules)

## Validation

Use the `verify_dist` target to enforce the spec:
```
cmake --build <builddir> --target verify_dist
```
`validate_dist` remains as a compatibility alias.

Checks include:
- required directories and leaf files
- forbidden chars and spaces
- max depth (<= 16 from `dist/`)
- required meta files
- optional manifest/file existence checks