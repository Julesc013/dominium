Status: DERIVED
Last Reviewed: 2026-02-01
Supersedes: none
Superseded By: none

# Setup Defaults and Build Flags

## Build options
- `SETUP_DEFAULT=ON` (default): `dominium-setup` maps to Setup.
- `SETUP_LEGACY_BUILD=ON`: legacy setup binaries remain buildable.
- `SETUP_LEGACY_DEPRECATED_WARN=ON`: emit a build warning when legacy targets are built.

## Default behavior
- `dominium-setup` is the default Setup CLI.
- Legacy binary is `dominium-setup-legacy` when legacy is enabled.
- Adapters and packaging scripts invoke Setup unless explicitly overridden.

## Example
```
cmake -S . -B build -DSETUP_DEFAULT=ON -DSETUP_LEGACY_BUILD=ON -DSETUP_LEGACY_DEPRECATED_WARN=ON
cmake --build build --target dominium-setup dominium-setup-legacy
```