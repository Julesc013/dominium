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
cmake --preset msvc-dev-debug
cmake --build --preset msvc-dev-debug
cmake --build --preset msvc-verify --target verify_fast
```

## VERIFY lane

- same mutation policy as DEV lane
- runs bounded and full verification explicitly
- no implicit release packaging

Canonical commands:

```
cmake --preset msvc-verify-full
cmake --build --preset msvc-verify-full --target verify_full
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
