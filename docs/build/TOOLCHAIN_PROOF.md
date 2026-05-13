# Toolchain Proof

Status: PROVISIONAL

Phase: POST-CONVERGE-10B

## Contract Toolchains

| Toolchain | Contract Status | Proof Level | Notes |
| --- | --- | --- | --- |
| `host_default` | unknown | configure-attempted | maps to detected VS2022 generator on this host |
| `msvc143` | planned | detected | Visual Studio Enterprise 2022 and C++ tools detected; configure fails on stale CMake source paths |
| `msvc145` | unknown | none | Visual Studio 18 2026 generator name is visible, but no instance is detected |
| `msvc141` | research | none | Visual Studio 15 2017 instance not detected |
| `msvc141_xp` | research | none | XP toolset not detected |
| `gcc` | planned | none | `gcc` and `g++` not detected |
| `clang` | planned | none | `clang`, `clang++`, and `clang-cl` not detected |
| `xcode9` | research | none | not a macOS host |
| `codewarrior9` | research | none | no CMake-native proof path |

## Local Probe Result

POST-CONVERGE-10B probe result on this machine:

| Tool | Detected? | Version/Detail | Notes |
| --- | --- | --- | --- |
| CMake | yes | `4.2.0` | generator names include Visual Studio 18 2026, 17 2022, 15 2017, Ninja, and others |
| Python | yes | `3.8.1` | sufficient for the build tools added in this task |
| Ninja | no | not found | not required for VS generator |
| Visual Studio 17 2022 | yes | Visual Studio Enterprise 2022 `17.14.37301.10` | canonical VS2022 instance detected |
| MSVC v143 | yes | CMake selected MSVC tools `14.44.35207`; compiler reports MSVC `19.44.35227.0` | tuple configure attempted |
| Windows SDK | yes | `10.0.26100.0` | selected by CMake |
| Visual Studio 18 2026 | no | no instance detected | generator name alone is not proof |
| Visual Studio 15 2017 | no | no instance detected | compatibility tuple blocked |
| Visual Studio 2015 | yes | legacy VS14 paths present | detected by direct path probe; not first proof lane |
| GCC/G++ | no | not found | Linux/host GCC tuple blocked |
| Clang/Clang++/clang-cl | no | not found | Clang tuple blocked |
| Xcode | no | not a macOS host | not applicable |

## Available Tuples

| Tuple | Proof Level | Notes |
| --- | --- | --- |
| `verify.winnt10.x64.msvc143.mt.debug` | detected | generated preset exists; configure attempted and failed during CMake generation |
| `verify.host.host.host_default.host.debug` | generated | host default maps to detected VS generator |
| `smoke.host.host.host_default.host.debug` | generated | host default maps to detected VS generator |

## Blocked Tuples

| Tuple | Reason |
| --- | --- |
| `verify.winnt10.x64.msvc145.mt.debug` | `msvc145` unavailable |
| `research.xp.x86.msvc141_xp.mt.release` | `msvc141_xp` unavailable |
| `verify.linux.x64.gcc.host.debug` | `gcc` unavailable |
| `verify.linux.x64.clang.host.debug` | `clang` unavailable |

No build or CTest proof exists yet. The first configure attempt reached MSVC/SDK selection and then failed on stale pre-convergence source paths in CMake test targets.
