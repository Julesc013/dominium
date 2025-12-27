# Windows Installer Matrix

| Windows version | Supported installers | UI modes | Notes |
| --- | --- | --- | --- |
| 3.0–3.11 | Win16 EXE | GUI (legacy), TUI (if console) | Legacy core profile; reduced capabilities |
| 95/98/ME | Win32 EXE | GUI/TUI/CLI | Legacy Win9x subset when required |
| NT 4.0 | Win32 EXE | GUI/TUI/CLI | MSI not available |
| 2000/XP (32-bit) | Win32 EXE, MSI x86 | GUI/TUI/CLI, MSI UI | MSI requires NT 5.0+ |
| XP x64 / Vista+ (64-bit) | Win64 EXE, MSI x64 | GUI/TUI/CLI, MSI UI | EXE provides MSI parity |
| Vista+ (32-bit) | Win32 EXE, MSI x86 | GUI/TUI/CLI, MSI UI | EXE provides MSI parity |

Legend:

- Win16 EXE: `DominiumSetup-win16.exe`
- Win32 EXE: `DominiumSetup-win32.exe`
- Win64 EXE: `DominiumSetup-win64.exe`

For feature parity rules and invocation guarantees, see:

- `docs/setup/WINDOWS_EXE_INSTALLER.md`
- `docs/setup/WINDOWS_MSI_INSTALLER.md`
- `docs/setup/INSTALLER_UX_CONTRACT.md`
