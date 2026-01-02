# Setup Adapter Matrix (SR-7)

| Adapter | OS Range | UI Modes | Operations | Ownership Model |
| --- | --- | --- | --- | --- |
| windows_exe | Windows NT5+ | gui, tui, cli | install, upgrade, repair, uninstall, verify, status | user/system/portable |
| windows_msi | Windows NT5+ | gui (MSI UI) | install, repair, uninstall | pkg-owned (system) |
| macos_pkg | macOS | gui (Installer) | install, repair, uninstall | pkg-owned (system) |
| linux_deb | Linux (deb) | cli | install, verify, status, uninstall | pkg-owned (system) |
| linux_rpm | Linux (rpm) | cli | install, verify, status, uninstall | pkg-owned (system) |
| steam | Steam runtime | cli | install, verify, repair, status | steam-owned |

Notes:
- Adapters are thin; they emit `install_request.tlv` and invoke `dominium-setup`.
- Ownership model is declared in the request and audited.
