Status: DERIVED
Last Reviewed: 2026-02-01
Supersedes: none
Superseded By: none

# SKU Model

Dominium SKUs are declared build metadata used to describe product intent and constraints.

## SKU Taxonomy

- `modern_desktop`: client/launcher/setup outputs for current desktop OS targets.
- `headless_server`: server outputs (no windowing/GPU/audio required).
- `devtools`: tools binaries intended for development workflows.
- `legacy_desktop`: explicit legacy desktop SKU (opt-in only).
- `unspecified`: fallback when no mapping or override exists.

## Selection Rules

Build metadata uses this precedence:

1) `DOM_BUILD_SKU` CMake cache override (when not `auto`).
2) Product mapping (when `DOM_BUILD_SKU=auto`):
   - `client` -> `modern_desktop`
   - `server` -> `headless_server`
   - `launcher` -> `modern_desktop`
   - `setup` -> `modern_desktop`
   - `tools` -> `devtools`

Legacy is never inferred. To declare legacy explicitly:

```
cmake -S . -B build/... -DDOM_BUILD_SKU=legacy_desktop
```

## Emission

- `--build-info` prints `sku=<value>` for all products.
- `dom_tool_artifactmeta` writes `identity.sku` using the same rules.