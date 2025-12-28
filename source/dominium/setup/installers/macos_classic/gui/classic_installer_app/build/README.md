Classic Installer Build Notes

This Classic installer app is intended for MPW/Think C or CodeWarrior-era toolchains.

Suggested steps (conceptual):
1) Compile `src/main.c` and `src/dialogs.c` as C89.
2) Compile `src/resources.r` with Rez to produce a resource fork.
3) Link with the legacy core sources from `core_legacy/src`.
4) Define `DSU_CLASSIC_MAC` to enable Dialog Manager code paths.

The app is a thin UI shell that collects parameters and calls the legacy core.
