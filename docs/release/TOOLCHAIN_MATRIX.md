Status: DERIVED
Last Reviewed: 2026-05-21
Supersedes: none
Superseded By: none

# Toolchain Matrix

Status: PROVISIONAL

Phase: CONVERGE-11

Machine-readable source: `contracts/release/component_matrix.contract.toml`

Build contract source:

- `contracts/build/floors.toml`
- `contracts/build/toolchains.toml`
- `contracts/build/tuples.toml`
- `contracts/build/artifacts.toml`

POST-CONVERGE-10 probe evidence is recorded in `docs/build/TOOLCHAIN_PROOF.md`.

## POST-CONVERGE-10 Local Probe

| Toolchain | Local Status | Notes |
| --- | --- | --- |
| msvc143 | blocked | Visual Studio 17 2022 instance not detected |
| msvc145 | blocked | Visual Studio 18 2026 instance not detected |
| msvc141 | blocked | Visual Studio 15 2017 instance not detected |
| gcc | blocked | `gcc`/`g++` and build tool not detected |
| clang | blocked | `clang`/`clang++`/`clang-cl` and build tool not detected |
| host_default | blocked | no usable compiler/build-tool pair detected |

No toolchain row is promoted by POST-CONVERGE-10.

## Baselines

- Engine/mainline C baseline: C17 with extensions off.
- Product/runtime/mainline C++ baseline: C++17 with extensions off.
- Public ABI remains C-compatible with opaque handles, versioned structs, explicit ownership, and no C++ ABI leakage.
- Platform and native SDK lanes must not alter engine determinism or product identity.

## Toolchain Rows

| Toolchain | Status | Tier | Phase | Families | Notes |
| --- | --- | --- | --- | --- | --- |
| msvc | provisional | T1 | desktop | windows, winnt | CMakePresets define MSVC/VS 2022 lanes; local availability is host-dependent. |
| gcc | provisional | T1 | desktop | linux, posix | Linux GCC lanes exist; support still requires preset, smoke, and package evidence. |
| clang | provisional | T1 | desktop | linux, macosx, posix, windows | Linux Clang and Windows clang-cl lanes exist. |
| xcode | planned | T1 | desktop | macosx | macOS Xcode lanes are declared; support requires host validation. |
| mingw | experimental | T2 | older | windows | Windows policy prefers MSVC; MinGW remains experimental. |

## Research And Back-Port Lanes

| Lane | Status | Tier | Phase | Families | Notes |
| --- | --- | --- | --- | --- | --- |
| legacy_vc6 | research | T3 | older | win9x, winnt | Retro lane requires frozen SDK/toolchain evidence and must not govern first-wave architecture. |
| freestanding_16bit | research | T3 | older | dos, win16 | Declared lane only; no support claim and not an active C17/C++17 floor. |

## Support Rule

No platform support may be claimed without:

- toolchain
- configure/build preset
- smoke test or validation gate
- package path
- docs naming the lane

Cross-host builds are provisional until deterministic build and package outputs are proven.
