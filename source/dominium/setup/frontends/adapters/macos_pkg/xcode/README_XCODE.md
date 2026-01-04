# Dominium Setup (macOS GUI) - Xcode Workflow

This project is a convenience layer for Interface Builder editing. CMake remains canonical.

## Open + Edit
- Open `source/dominium/setup/frontends/adapters/macos_pkg/xcode/DominiumSetupMac.xcodeproj`.
- UI is in `source/dominium/setup/frontends/adapters/macos_pkg/xcode/DominiumSetupMacApp/Resources/Base.lproj/Main.storyboard`.
- Sources are in `source/dominium/setup/frontends/adapters/macos_pkg/xcode/DominiumSetupMacApp/Sources`.

## Debug Sandbox
Set these scheme environment variables for safe runs:
- `DOMINIUM_SETUP_SANDBOX_ROOT=/tmp/dominium_setup_gui`
- `DOMINIUM_SETUP_USE_FAKE_SERVICES=1`
- `DOMINIUM_SETUP_MANIFEST=<repo>/source/dominium/setup/tests/fixtures/manifests/minimal.dsumanifest`

Outputs land in the sandbox root (`install_request.tlv`, `install_plan.tlv`, `installed_state.tlv`, `setup_audit.tlv`, `job_journal.tlv`).

## Headless Request Export
The app supports a hidden CLI mode:
```
dominium-setup-macos-gui --export-request --manifest <path> --op install --scope user \
  --platform macos-x64 --out-request /tmp/install_request.tlv
```

## Guardrails
- The GUI emits `install_request.tlv` and calls `dominium-setup`; it does not embed install logic.
- Mirror any Xcode-only settings into CMake (or document them as local-only).
