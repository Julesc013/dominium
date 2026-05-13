# Toolchain Proof

Status: PROVISIONAL

Phase: POST-CONVERGE-10

## Contract Toolchains

| Toolchain | Contract Status | Proof Level | Notes |
| --- | --- | --- | --- |
| `host_default` | unknown | none | no compiler/build-tool pair detected locally |
| `msvc143` | planned | none | Visual Studio 17 2022 instance not detected |
| `msvc145` | unknown | none | Visual Studio 18 2026 generator name is visible, but no instance is detected |
| `msvc141` | research | none | Visual Studio 15 2017 instance not detected |
| `msvc141_xp` | research | none | XP toolset not detected |
| `gcc` | planned | none | `gcc` and `g++` not detected |
| `clang` | planned | none | `clang`, `clang++`, and `clang-cl` not detected |
| `xcode9` | research | none | not a macOS host |
| `codewarrior9` | research | none | no CMake-native proof path |

## Local Probe Result

POST-CONVERGE-10 probe result on this machine:

| Tool | Detected? | Version/Detail | Notes |
| --- | --- | --- | --- |
| CMake | yes | `4.2.0` | generator names include Visual Studio 18 2026, 17 2022, 15 2017, Ninja, and others |
| Python | yes | `3.8.1` | sufficient for the build tools added in this task |
| Ninja | no | not found | blocks Ninja fallback tuples |
| Visual Studio 17 2022 | no | no instance detected | canonical `verify` remains blocked locally |
| Visual Studio 18 2026 | no | no instance detected | generator name alone is not proof |
| Visual Studio 15 2017 | no | no instance detected | compatibility tuple blocked |
| GCC/G++ | no | not found | Linux/host GCC tuple blocked |
| Clang/Clang++/clang-cl | no | not found | Clang tuple blocked |
| Xcode | no | not a macOS host | not applicable |

## Available Tuples

None on this machine.

## Blocked Tuples

| Tuple | Reason |
| --- | --- |
| `verify.host.host.host_default.host.debug` | `host_default` unavailable |
| `smoke.host.host.host_default.host.debug` | `host_default` unavailable |
| `verify.winnt10.x64.msvc143.mt.debug` | `msvc143` unavailable |
| `verify.winnt10.x64.msvc145.mt.debug` | `msvc145` unavailable |
| `research.xp.x86.msvc141_xp.mt.release` | `msvc141_xp` unavailable |
| `verify.linux.x64.gcc.host.debug` | `gcc` unavailable |
| `verify.linux.x64.clang.host.debug` | `clang` unavailable |

No configure/build/test proof exists yet.
