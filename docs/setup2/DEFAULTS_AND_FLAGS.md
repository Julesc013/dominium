# Setup2 Defaults and Build Flags

## Build options
- `SETUP2_DEFAULT=ON` (default): `dominium-setup` maps to Setup2.
- `SETUP_LEGACY_BUILD=ON`: legacy setup binaries remain buildable.
- `SETUP_LEGACY_DEPRECATED_WARN=ON`: emit a build warning when legacy targets are built.

## Default behavior
- `dominium-setup` resolves to `dominium-setup2`.
- Legacy binary is `dominium-setup-legacy` when legacy is enabled.
- Adapters and packaging scripts invoke Setup2 unless explicitly overridden.

## Example
```
cmake -S . -B build -DSETUP2_DEFAULT=ON -DSETUP_LEGACY_BUILD=ON -DSETUP_LEGACY_DEPRECATED_WARN=ON
cmake --build build --target dominium-setup2 dominium-setup-legacy
```
