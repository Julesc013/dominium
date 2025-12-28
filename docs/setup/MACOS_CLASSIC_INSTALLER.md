Mac OS Classic Installer

Overview
- Classic Mac OS uses a legacy Setup Core profile (C89-friendly) that performs install logic.
- The installer GUI is a thin, period-correct shell that collects choices and invokes the legacy core.
- The legacy core emits installed-state in DSUS TLV format for compatibility/import.

Supported OS Bands
- Band A: Mac OS 8.1-9.2.2 (HFS+)
- Band B: System 7.x / Mac OS 7.x (HFS)
- System 6 is aspirational and not guaranteed.

Installer Flow (UX Contract Mapping)
- Welcome
- Install Type: Easy vs Custom
- Destination selection
- Component selection (Custom)
- Summary
- Progress
- Completion

Operations
- Detect (state presence)
- Install (default)
- Repair (reinstall from payloads)
- Uninstall (remove owned files)
- Verify (existence + size checks)
  - Detect checks for the installed-state file only.

Installed-State
- Format: DSUS (TLV, compatible with modern launcher import rules).
- Default location (GUI): `Preferences:Dominium:dominium_state.dsus`
- Logs: `Preferences:Dominium:dominium_install.log`

CLI (where feasible)
```
ClassicSetup --install --manifest Manifests/dominium_full.dsumanifest --payload-root Payloads --install-root "Applications:Dominium" --state "Preferences:Dominium:dominium_state.dsus"
ClassicSetup --repair --manifest Manifests/dominium_full.dsumanifest --payload-root Payloads
ClassicSetup --uninstall --state "Preferences:Dominium:dominium_state.dsus"
ClassicSetup --verify --state "Preferences:Dominium:dominium_state.dsus"
ClassicSetup --detect --state "Preferences:Dominium:dominium_state.dsus"
```

Packaging
- Disk image layout is prepared under `source/dominium/setup/installers/macos_classic/packaging/sit_or_img/layout`.
- Use `build_image.sh` on macOS to produce an HFS image.

Emulator Testing (Manual)
- Basilisk II:
  - Add the built .img to the emulator disk list.
  - Boot, open the mounted image, and run the installer app.
  - Confirm `Preferences:Dominium:dominium_state.dsus` exists.
- SheepShaver:
  - Mount the disk image, run the installer, then reboot if required.
  - Verify the installed files in the target folder and the log/state files.
