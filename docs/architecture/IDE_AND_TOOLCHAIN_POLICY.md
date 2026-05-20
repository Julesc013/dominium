Status: CANONICAL
Last Reviewed: 2026-05-21
Supersedes: prior legacy/modern mixed toolchain matrix
Superseded By: none
Stability: provisional
Future Series: LANGUAGE-BASELINE, PORTABILITY-MATRIX
Replacement Target: canon-aligned documentation set for convergence and release preparation

# IDE and Toolchain Policy

Status: binding.

Scope: IDE projections, toolchain tiers, OS floor, ABI policy, and active
language baseline.

## Active Floor

- Windows: Windows 7 SP1 or newer.
- macOS: macOS 10.9.5 or newer.
- Linux: supported by a C17/C++17-capable GCC/Clang toolchain and documented
  libc/libstdc++/libc++ floor.

The active language baseline is C17 and C++17 with extensions off.

## Windows

- Win7 SP1 and newer: C17/C++17 mainline; pinned SDK; avoid post-target APIs.
- Win10/11: C17/C++17 mainline; separate artifacts per toolchain where needed.
- Win95/98/ME, NT4/2000, XP, and Vista lanes are retired from active mainline
  and may exist only as historical or future retro research surfaces.

## macOS

- macOS 10.9.5 and newer: C17/C++17 mainline.
- C++17 standard-library use is restricted for macOS 10.9.5 compatibility; do
  not require `std::filesystem`, `std::pmr`, `std::to_chars`, `std::from_chars`,
  `std::any`, or unguarded throwing optional/variant access paths.
- Classic Mac OS and early OS X lanes are retired from active mainline and may
  exist only as historical or future retro research surfaces.

## Linux

- Active Linux builds use C17/C++17-capable GCC or Clang.
- The real binary floor is the libc/libstdc++/libc++ policy, not the distro
  name.
- GCC 2.95 and legacy Linux lanes are retired from active mainline and may
  exist only as historical or future retro research surfaces.

## Global Warnings

- C standard != OS compatibility.
- Compiler defines ABI reality.
- SDK silently raises OS floor.
- Never mix CRTs across module boundaries.
- Never pass STL/allocator objects across stable public ABI boundaries.
- Never share binaries across OS families.
- C17/C++17 mainline permanently drops active support for Win9x, NT4/2000, XP,
  Classic Mac OS, and early OS X.
- Legacy tiers are frozen only when a future retro lane explicitly validates
  them; they do not govern mainline development.
