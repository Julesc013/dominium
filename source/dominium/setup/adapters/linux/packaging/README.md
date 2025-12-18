# Linux Packaging Templates (Plan S-6)

These files are **templates** for downstream packagers. They are intentionally minimal.

Rules:

- maintainer scripts must do **parameter passing only** (no business logic)
- all installation decisions (component selection, install roots, determinism) must come from Setup Core inputs
- platform integrations should be executed through `dsu_platform_iface` (via `dominium-setup-linux platform-register/unregister`)

