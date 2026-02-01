Status: DERIVED
Last Reviewed: 2026-02-01
Supersedes: none
Superseded By: none

# Transition Do-Not List

These constraints prevent toolchain lock-in and interface rot.

## Do Not

- Do not assume a single compiler vendor (MSVC/GCC/Clang are all valid).
- Do not couple OS floors to language standards (C89/C++98 vs C17/C++17).
- Do not bake CRT/libc assumptions into engine/game ABI.
- Do not change the global build number or per-product semver scheme.
- Do not embed assets in binaries (zero-pack boot remains required).
- Do not add GUI/TUI dependencies to tests (CLI-only remains canonical).
- Do not let apps/tools include engine private headers or link engine internals.

## Preserve

- Artifact filename identity scheme.
- Toolchain descriptor output and fields.
- Stable CLI contracts and protocol/API/ABI version reporting.