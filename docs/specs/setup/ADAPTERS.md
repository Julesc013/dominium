# Setup Adapters (SR-7)

Setup adapters are thin frontends. They only collect choices, emit `install_request.tlv`, and invoke the kernel (direct API or `dominium-setup`). They must not implement install logic.

## Common outputs
- `install_request.tlv`
- `install_plan.tlv`
- `job_journal.tlv`
- `setup_audit.tlv`
- `installed_state.tlv` (after successful apply)

## Adapters
- Windows EXE: `dominium-setup-win-exe` (GUI/TUI/CLI; delegates to `dominium-setup`).
- Windows MSI wrapper: WiX skeleton that invokes `dominium-setup` via custom action.
- macOS PKG wrapper: `postinstall` script invokes `dominium-setup`.
- Linux DEB wrapper: `postinst/prerm` scripts invoke `dominium-setup` in safe modes.
- Linux RPM wrapper: `postinst/prerm` scripts invoke `dominium-setup` in safe modes.
- Steam provider: `dominium-setup-steam` generates Steam-owned requests.

## Windows EXE example
Silent CLI install:
```
dominium-setup-win-exe --cli run --manifest manifest.tlv --op install --scope system --root install --payload-root payloads --out-request install_request.tlv --out-plan install_plan.tlv --out-state installed_state.tlv --out-audit setup_audit.tlv --out-journal job_journal.tlv --deterministic 1
```

Request emission only:
```
dominium-setup-win-exe --cli request-make --manifest manifest.tlv --op install --scope system --out-request install_request.tlv --deterministic 1
```

All adapters set:
- `frontend_id`
- `ui_mode`
- `target_platform_triple` (explicit or via services)
- `requested_splat_id` when applicable
