Status: DERIVED
Last Reviewed: 2026-02-01
Supersedes: none
Superseded By: none

# OS Floor Policy

OS floors are explicit build declarations. They are not inferred from compiler or language mode.

## Declaration

Use these CMake cache variables:

- `DOM_TARGET_OS_FAMILY` (e.g., `winnt`, `linux`, `macosx`)
- `DOM_TARGET_OS_MIN` (e.g., `win10_1507`, `glibc_2.17`, `11.0`)

The emitted field is:

```
toolchain_os_floor=<family>:<min>
```

If either value is missing, the floor is reported as `unspecified`.

## Canonical Examples

- `winnt:win10_1507`
- `linux:glibc_2.17`
- `linux:musl_1.2`
- `macosx:11.0`

## Rules

- Floors are declarations, not promises.
- Floors are not derived from C/C++ language standards.
- Legacy floors must be declared explicitly (never inferred).