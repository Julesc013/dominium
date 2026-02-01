Status: CANONICAL
Last Reviewed: 2026-02-01
Supersedes: none
Superseded By: none

# IDE and Toolchain Policy (REPOX)





Status: binding.


Scope: IDE projections, toolchain tiers, and OS/ABI policy.





This document is the authoritative toolchain × OS × language matrix.





## Windows


- Win95/98/ME: VC6 SP6; C89/C++98; /MT only; ANSI Win32; Unicode forbidden; separate binaries from NT builds.


- NT4/2000: VC6 SP6; C89/C++98; NT-only binaries; CRT legacy behavior.


- XP/Vista: VC7.1; C89/C++98; static CRT required; do NOT extend VC6 into this tier.


- Win7/8/8.1: VS2015 U3; C89/C++98; pinned SDK; avoid post-target APIs.


- Win10/11: VS2015 U3 (legacy) + VS2026 (modern); legacy C89/C++98; modern C17/C++17; separate artifacts per toolchain.





## Mac


- Classic (System 7–9): CodeWarrior Classic 10; C89/C++98; PPC only; Classic Toolbox/Carbon optional; no binary overlap with OS X.


- OS X/macOS: Xcode era-pinned; early C89/C++98; modern C17/C++17; SDK removal is expected; multiple frozen envs required; Carbon dead-end.





## Linux


- Kernel 2.2 → current: GCC 2.95 → GCC/Clang; legacy C89/C++98; modern C17/C++17; real floor is glibc; avoid distro assumptions.





## Global warnings (law)


- C standard != OS compatibility.


- Compiler defines ABI reality.


- SDK silently raises OS floor.


- Never mix CRTs across module boundaries.


- Never pass STL/allocator objects across DLL boundaries.


- Never share binaries across OS families.


- Transition to C17/C++17 permanently drops: Win9x, NT4/2000, XP, Classic Mac OS, early OS X.


- Legacy tiers are frozen once validated.





## Projection policy


- IDE projections are generated from CMake + REPOX scripts.


- Toolchain tier, OS family, and language mode are explicit inputs.


- No IDE is a source of truth; the repository owns the build graph.





## Cross-references


- `docs/architecture/REPO_OWNERSHIP_AND_PROJECTIONS.md`


- `docs/architecture/PROJECTION_LIFECYCLE.md`
