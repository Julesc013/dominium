# Setup2 Adapters (SR-7)

Setup2 adapters are thin frontends. They only collect choices, emit `install_request.tlv`, and invoke the kernel (direct API or `dominium-setup2`). They must not implement install logic.

## Common outputs
- `install_request.tlv`
- `install_plan.tlv`
- `job_journal.tlv`
- `setup_audit.tlv`
- `installed_state.tlv` (after successful apply)

## Adapters
- Windows EXE: `dominium-setup2-win-exe` (GUI/TUI/CLI; delegates to `dominium-setup2`).
- Windows MSI wrapper: WiX skeleton that invokes `dominium-setup2` via custom action.
- macOS PKG wrapper: `postinstall` script invokes `dominium-setup2`.
- Linux DEB wrapper: `postinst/prerm` scripts invoke `dominium-setup2` in safe modes.
- Linux RPM wrapper: `postinst/prerm` scripts invoke `dominium-setup2` in safe modes.
- Steam provider: `dominium-setup2-steam` generates Steam-owned requests.

## Windows EXE example
Silent CLI install:
```
dominium-setup2-win-exe --cli run --manifest manifest.tlv --op install --scope system --root install --payload-root payloads --out-request install_request.tlv --out-plan install_plan.tlv --out-state installed_state.tlv --out-audit setup_audit.tlv --out-journal job_journal.tlv --deterministic 1
```

Request emission only:
```
dominium-setup2-win-exe --cli request-make --manifest manifest.tlv --op install --scope system --out-request install_request.tlv --deterministic 1
```

All adapters set:
- `frontend_id`
- `ui_mode`
- `target_platform_triple` (explicit or via services)
- `requested_splat_id` when applicable
