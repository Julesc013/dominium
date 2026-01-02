# Packaging Defaults

Setup2 is the default installer system for all new packaging outputs.

## Required behavior
- Adapters emit `install_request.tlv` with `frontend_id`, `ui_mode`, and `target_platform_triple`.
- Packaging scripts invoke Setup2 (`dominium-setup2` or kernel API).
- Legacy setup may only be used with explicit overrides.

## Override policy
- Legacy packaging requires an explicit flag in build scripts.
- CI scripts fail when legacy binaries are referenced without override.

## Verification
```
cmake --build build --target setup2-adapters
scripts/release/run_setup2_release_gate.bat
```
