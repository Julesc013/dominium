# Toolchain Matrix

Status: PROVISIONAL

Phase: CONVERGE-11

Machine-readable source: `contracts/release/component_matrix.contract.toml`

## Baselines

- Engine baseline: C89/C90 with extensions off.
- Product shell baseline: C++98 with extensions off.
- Platform and native SDK lanes must not alter engine determinism or product identity.

## Toolchain Rows

| Toolchain | Status | Tier | Families | Notes |
| --- | --- | --- | --- | --- |
| msvc | provisional | T1 | windows, winnt | CMakePresets define MSVC/VS 2022 lanes; local availability is host-dependent. |
| gcc | provisional | T1 | linux, posix | Linux GCC lanes exist; support still requires preset, smoke, and package evidence. |
| clang | provisional | T1 | linux, macosx, posix, windows | Linux Clang and Windows clang-cl lanes exist. |
| xcode | planned | T1 | macosx | macOS Xcode lanes are declared; support requires host validation. |
| mingw | experimental | T2 | windows | Windows policy prefers MSVC; MinGW remains experimental. |
| legacy_vc6 | research | T3 | win9x, winnt | Retro lane requires frozen SDK/toolchain evidence. |
| freestanding_16bit | research | T3 | dos, win16 | Declared lane only; no support claim. |

## Support Rule

No platform support may be claimed without:

- toolchain
- configure/build preset
- smoke test or validation gate
- package path
- docs naming the lane

Cross-host builds are provisional until deterministic build and package outputs are proven.
