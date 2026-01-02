# Setup Parity Lock Matrix (SR-11)

This matrix is the authoritative parity map across frontends and adapters. Any divergence
from the parity rules must be explicitly documented here and asserted by tests.

## Matrix

| Adapter | Operations | Scopes | Ownership | UI modes | Known limitations |
| --- | --- | --- | --- | --- | --- |
| CLI (`dominium-setup`) | install/upgrade/repair/uninstall/verify/status | user/system/portable | any | cli (request can set gui/tui/cli) | none |
| TUI (`dominium-setup-tui`) | install/repair/uninstall/verify/status | user/system/portable | any | tui | no upgrade prompt; wizard only |
| Windows EXE (`dominium-setup-win-exe`) | install/upgrade/repair/uninstall/verify/status | user/system/portable | any | gui/tui/cli | NT5+ only; GUI wizard stub falls back to console prompts |
| Windows MSI wrapper | install/repair/uninstall (via MSI UI) | user/system | pkg/portable | gui (MSI) | wrapper_no_request; MSI UI limits choices |
| macOS PKG wrapper | install (quick defaults); repair/verify via CLI | user/system | pkg/portable | gui (Installer) | wrapper_no_request; advanced options via CLI/TUI |
| Linux deb wrapper | install/remove via pkgmgr; verify/status via maintainer scripts | system | pkg | none | wrapper_no_request; no custom UI |
| Linux rpm wrapper | install/remove via pkgmgr; verify/status via maintainer scripts | system | pkg | none | wrapper_no_request; no custom UI |
| Steam provider (`dominium-setup-steam`) | install/repair/verify/status | user | steam | cli | uses Steam ownership + splat_steam; parity tests require manifest target=steam |

## Parity Lock Records (machine)

adapter=cli group=core_cli ops=install,upgrade,repair,uninstall,verify,status scopes=user,system,portable ownership=any ui=cli,tui,gui limitations=none
adapter=tui group=core_tui ops=install,repair,uninstall,verify,status scopes=user,system,portable ownership=any ui=tui limitations=no_upgrade_prompt
adapter=windows_exe group=core_cli ops=install,upgrade,repair,uninstall,verify,status scopes=user,system,portable ownership=any ui=gui,tui,cli limitations=nt5_plus_gui_stub
adapter=windows_msi group=wrapper ops=install,repair,uninstall scopes=user,system ownership=pkg,portable ui=gui limitations=wrapper_no_request
adapter=macos_pkg group=wrapper ops=install,repair,verify scopes=user,system ownership=pkg,portable ui=gui limitations=wrapper_no_request
adapter=linux_deb group=wrapper ops=install,uninstall,verify,status scopes=system ownership=pkg ui=none limitations=wrapper_no_request
adapter=linux_rpm group=wrapper ops=install,uninstall,verify,status scopes=system ownership=pkg ui=none limitations=wrapper_no_request
adapter=steam group=steam_cli ops=install,repair,verify,status scopes=user ownership=steam ui=cli limitations=steam_owned_only;steam_manifest_target=steam
