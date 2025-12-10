# Retro / Legacy Installers

Dominium supports legacy targets with lightweight text installers instead of
modern MSI/pkg/deb tooling. These installers mirror the layout used on modern
platforms so saves/data/mods remain compatible when copied.

## Common layout
- Install root: user-chosen directory (default `C:\DOMINIUM` or equivalent).
- `bin/` — executables and launchers.
- `data/` — shipped data packs. User saves/configs may also live here depending
  on platform constraints.
- Optional launcher script/batch is written at the install root to start the
  game from `bin/`.

There is no system-vs-user split on these systems; the chosen directory is the
install.

## DOS (16/32-bit)
- Installer: `source/dominium/setup/os/dos/setup_dos_tui.c`
  (text UI).
- Prompts for target (default `C:\DOMINIUM`), offers Install/Repair/Uninstall.
- Copies payload from the current media to `bin/` and `data/` under the target.
- Writes `DOMINIUM.BAT` in the target that launches `bin\dominium.exe`.

## Win16
- Stub: `source/dominium/setup/os/win16/setup_win16_tui.c`.
- Intended behavior: simple dialog/TUI, prompt for target, copy files, and add a
  Program Manager group or PIF/shortcut pointing to the launcher in `bin/`.

## CP/M-80 / CP/M-86
- Stubs: `source/dominium/setup/os/cpm/setup_cpm80.c`,
  `setup_cpm86.c`.
- Intended behavior: prompt for drive/user area, copy COM/EXE payload, and
  create a SUBMIT script to launch the game with the chosen install directory.

## Carbon OS (Z80)
- Stub: `source/dominium/setup/os/carbon/setup_carbon.c`.
- Intended behavior: prompt for volume/path, copy binaries/data, and register
  with Carbon’s launcher (if available).

## Notes
- These installers do not use `dominium-setup-cli` due to dependency and OS
  constraints.
- Keep file names/layout consistent with modern installs so assets and saves can
  be shared manually between systems.
