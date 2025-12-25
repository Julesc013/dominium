# Build Output Guide (dist/)

This repo routes final link artifacts directly into `dist/`. Build intermediates
remain inside `build/*` only.

## Layout Summary (Frozen)

Top-level:
- `dist/meta/{dist.json,targets.json,files.json,build.txt,ver.txt,hash.txt,rules.txt}`
- `dist/docs/{readme.txt,licenses.txt,notes.txt}`
- `dist/res/{common,locale,packs}`
- `dist/cfg/{default,profiles,schemas}`
- `dist/sys/<os>/<arch>/...`
- `dist/pkg/{win,mac,linux,android,ios,web}`
- `dist/redist/{msvc,dx,other}`
- `dist/sym/<os>/<arch>/...` (symbols only)

Leaf contract:
```
dist/sys/<os>/<arch>/
  bin/launch/
  bin/game/
  bin/engine/
  bin/rend/
  bin/tools/
  bin/share/
  lib/
  etc/
  man/
```

Required leaf files:
- `dist/sys/<os>/<arch>/etc/leaf.json`
- `dist/sys/<os>/<arch>/man/readme.txt`

Naming rules:
- Directory charset: `[a-z0-9_]` (lowercase, no spaces)
- Filename charset: `[a-z0-9_.-]` (lowercase, no spaces)
- No DOS device basenames (con, prn, aux, nul, com1..9, lpt1..9)
- No version numbers in filenames
- Max depth from `dist/` is 16

## Runtime Seed (Portable/User/System)

For rapid local testing, the build can seed a minimal runtime layout under the
active leaf:
- `dist/sys/<os>/<arch>/.dsu/installed_state.dsustate`
- `dist/sys/<os>/<arch>/dominium_install.json`
- `dist/sys/<os>/<arch>/repo/{products,packs,mods}`
- `dist/sys/<os>/<arch>/{instances,artifacts,audit,exports,temp}`
Note: `.dsu` is a reserved seed directory (dot-prefix exception).

Enable/disable:
- `-DDOM_DIST_SEED_RUNTIME=ON|OFF` (default: ON)

Install type + channel:
- `-DDOM_DIST_INSTALL_TYPE=portable|user|system` (default: portable)
- `-DDOM_DIST_BUILD_CHANNEL=dev|beta|stable` (default: dev)

Generate/refresh:
```
cmake --build <builddir> --target dist_seed
```

## Build Directories (Recommended)

```
build/msvc-debug/
build/msvc-release/
build/msys2-debug/
build/msys2-release/
```

## Configure + Build

MSVC x64 (Visual Studio generator):
```
cmake --preset msvc-debug
cmake --build --preset msvc-debug
```

MSYS2 x64 (Ninja):
```
cmake --preset msys2-debug
cmake --build --preset msys2-debug
```

## Verify Output

```
cmake --build <builddir> --target verify_dist
```

This checks layout, naming, forbidden intermediates, and prints the expected
`dist/sys/winnt/x64` subtree summary.

## Variant Axis (Optional)

To allow toolchains to co-exist under the same `dist/` root:
```
cmake -S . -B build/msvc-debug -DDOM_DIST_VARIANT=msvc
cmake -S . -B build/msys2-debug -DDOM_DIST_VARIANT=msys2
```

This adds:
```
dist/sys/<os>/<arch>/<variant>/
dist/sym/<os>/<arch>/<variant>/
```
