# SR-7 Status: Thin Platform Adapters

SR-7 adds thin platform adapters that emit `install_request.tlv` and invoke the setup2 kernel via `dominium-setup2`.

## Added
- Adapter scaffolding under `source/dominium/setup/frontends/adapters/`.
- Windows EXE adapter (`dominium-setup2-win-exe`) with CLI/TUI/GUI stubs.
- Windows MSI WiX skeleton.
- macOS PKG wrapper scripts.
- Linux DEB/RPM wrapper scripts.
- Steam provider adapter (`dominium-setup2-steam`).
- Adapter conformance tests for Windows EXE and Steam.
- Adapter docs and matrix.

## Still Stubbed
- Windows EXE GUI is a placeholder dialog.
- MSI/PKG/DEB/RPM targets only stage wrapper sources.
- Steam integration is a stub (no real Steam API hooks).

## No Behavior Changes
- Kernel logic remains authoritative.
- Adapters do not implement install logic.
