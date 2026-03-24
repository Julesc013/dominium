Status: DERIVED
Last Reviewed: 2026-02-09
Supersedes: none
Superseded By: none

# Build Lanes

## DEV lane

- `build_kind=dev`
- `build_gbn=none`
- build identity uses BII (`dev.<bii>`)
- default build target is `all_runtime`
- default verification target is `verify_fast`
- packaging and `dist_*` targets are not part of default flow

Canonical commands:

```
Windows:
  cmake --preset local
  cmake --build --preset local
  cmake --build --preset verify --target verify_fast

Linux:
  cmake --preset linux-gcc-dev
  cmake --build --preset linux-gcc-dev
  cmake --build --preset linux-verify --target verify_fast

macOS:
  cmake --preset macos-dev
  cmake --build --preset macos-dev
  cmake --build --preset macos-verify --target verify_fast
```

## VERIFY lane

- same mutation policy as DEV lane
- runs bounded and full verification explicitly
- no implicit release packaging

Canonical commands:

```
Windows:
  cmake --preset verify
  cmake --build --preset verify --target verify_full

Linux:
  cmake --preset linux-verify
  cmake --build --preset linux-verify --target verify_full

macOS:
  cmake --preset macos-verify
  cmake --build --preset macos-verify --target verify_full
```

## RELEASE lane

- `build_kind` must be one of `release|beta|rc|hotfix`
- packaging targets are enabled only through explicit `dist_*` targets
- `DOM_BUILD_GBN` must be present and not `none` for `dist_*` targets
- release lane must pass `verify_full` before `dist_all`

Canonical commands:

```
cmake --preset release-winnt-x86_64 -DDOM_BUILD_GBN=<allocated_gbn>
cmake --build --preset release-winnt-x86_64 --target verify_full
cmake --build --preset release-winnt-x86_64 --target dist_all
```

Advanced preset surface:
- Set `DOMINIUM_ADVANCED_PRESETS=1` before configure if you need non-default toolchains, legacy lanes, or IDE projection presets.
