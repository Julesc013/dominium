# Windows Legacy Support (Win16/Win9x)

This document captures legacy Windows installer profiles. For deep legacy DOS/Win3.x/Win9x,
see `docs/setup/DOS_INSTALLER.md`, `docs/setup/WIN3X_INSTALLER.md`,
`docs/setup/WIN9X_INSTALLER.md`, and `docs/setup/WINDOWS_LEGACY_MATRIX.md`.

## Scope

- Win16 (Windows 3.x): `DominiumSetup-win16.exe`
- Win32 legacy (Windows 95/98/ME): `DominiumSetup-win32.exe` in Win9x profile when required

## Legacy Setup Core profile

Legacy builds use a reduced Setup Core profile (`dominium-setup-legacy` or a
Win9x-compatible build of `dominium-setup`) with the following constraints:

- No long paths; 8.3 path fallbacks only.
- No Unicode-only APIs; ANSI codepaths only.
- No modern cryptography beyond digest32/digest64.
- Limited component graph resolution (no complex conflicts).
- Reduced verification and repair (basic file presence and size checks).

## Installed-state compatibility

Legacy installers still emit an installed-state file compatible with modern
Setup Core readers. Unknown TLVs are skipped, and unavailable fields are omitted.

Default location (EXE legacy profile):

- `<install_root>/.dsu/installed_state.dsustate`

Deep legacy installers (DOS/Win3.x/Win9x) use:

- `<install_root>\dominium_state.dsus`

## Build tooling notes

The Win16 EXE is built with an external 16-bit toolchain and is not built by
default in the modern MSVC CMake environment. The `setup_exe_win16` target
prints guidance and defers to the legacy toolchain workflow documented here.

## Known limitations

- TUI mode may be unavailable on systems without a usable console.
- No MSI integration or MSI-based detection.
- Limited registry integration; shortcuts/associations are applied via legacy
platform interfaces only when requested.

See also:

- `docs/setup/WINDOWS_EXE_INSTALLER.md`
- `docs/setup/INVOCATION_PAYLOAD.md`
