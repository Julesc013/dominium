# Pacman Packaging (Stub)

Arch/pacman packaging is optional. This directory intentionally contains a
minimal stub so the Linux installer suite has a documented placeholder.

Recommended approach:

- Create a `PKGBUILD` that stages `artifact_root/` under `/opt/dominium/`.
- Use `dominium-setup` in a post-install hook to install/repair.
- Use `dominium-setup-linux platform-register/unregister` for desktop entries.

See `docs/setup/LINUX_PACKAGING.md` for the ownership model and lifecycle.
