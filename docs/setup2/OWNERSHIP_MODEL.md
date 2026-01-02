# Setup2 Ownership Model (SR-7)

Ownership controls which system is responsible for install/remove actions.

## portable
- Kernel-owned files under a portable install root.
- Full lifecycle (install/repair/uninstall) is handled by setup2.
- Suitable for user-space and offline installs.

## pkg
- Package manager owns core runtime files.
- Setup2 may only manage add-on packs/mods or user data outside pkg-owned paths.
- Maintainer scripts should avoid heavy mutation; use verify/status and state updates only.

## steam
- Steam owns game files inside the Steam library.
- Setup2 can verify/repair using Steam hooks and manage user data.
- Reinstall/uninstall must respect Steam ownership boundaries.

## any
- No explicit ownership preference; kernel selects compatible SPLAT.
