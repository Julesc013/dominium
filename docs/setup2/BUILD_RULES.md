# BUILD_RULES

- Layer 0 (dsk_kernel) is OS-API-free and side-effect-free; it may only call services via vtables.
- Layer 1 (dss_services) owns OS headers and platform libraries behind compile guards.
- Layer 2 (frontends) may do IO via services but may not implement install logic.

Enforcement:
- dsk_kernel compiles with `DSK_FORBID_OS_HEADERS=1` and includes `dsk_forbidden_includes.h`.
- `scripts/setup2/check_kernel_purity.(bat|sh)` scans kernel sources for forbidden headers.
- CTest runs the `setup2_kernel_purity_check` test to validate purity.

Adding new services:
- Define vtable in `source/dominium/setup/services/include/dss/`.
- Implement real + fake backends under `source/dominium/setup/services/src/`.
- Update `dss_services.cpp` wiring and `docs/setup2/SERVICES_FACADES.md`.
