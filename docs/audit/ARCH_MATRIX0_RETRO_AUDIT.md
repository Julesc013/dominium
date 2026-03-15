Status: DERIVED
Last Reviewed: 2026-03-14
Stability: provisional
Future Series: PLATFORM/DIST
Replacement Target: release-pinned target matrix and release-index availability model

# ARCH-MATRIX-0 Retro Audit

Fingerprint: `2e3abb7d328514a447278e0557a4ad3d7fe7ff9bc54cbdaf1bdfccca74b10abc`

## Existing Inputs

- `data/registries/platform_capability_registry.json` already declares platform-family capability envelopes.
- `schema/release/release_index.schema` already exposes `platform_matrix` rows with `{os, arch, abi, artifact_url_or_path}`.
- `data/registries/install_profile_registry.json` already defines deterministic install profiles for full/client/server/tools/sdk.
- CAP-NEG endpoint descriptors now expose `official.target_id`, `official.os_id`, `official.arch_id`, `official.abi_id`, and `official.target_tier`.

## Currently Built Targets

- `win64` -> `target.os_winnt.abi_msvc.arch_x86_64` (`tier 1`; source `dist`)

## Declared but Unbuilt / Aspirational Targets

- `target.os_bsd.abi_null.arch_x86_64` (`tier 3`) -> platform `none`; known gaps: No BSD bundle or adapter lane is shipped in v0.0.0-mock.
- `target.os_linux.abi_glibc.arch_arm64` (`tier 2`) -> platform `platform.linux_gtk`; known gaps: No ARM64 Linux portable bundle is built in the current repository state.
- `target.os_linux.abi_glibc.arch_x86_64` (`tier 1`) -> platform `platform.linux_gtk`; known gaps: Linux x86_64 is Tier 1 only when a bundle is actually built and validated.
- `target.os_macos_classic.abi_carbon.arch_ppc32` (`tier 3`) -> platform `platform.macos_classic`; known gaps: Classic Mac remains declared only; no Carbon package or validation lane exists.
- `target.os_macosx.abi_cocoa.arch_arm64` (`tier 2`) -> platform `platform.macos_cocoa`; known gaps: No macOS universal bundle is built in the current repository state.
- `target.os_msdos.abi_freestanding.arch_x86_32` (`tier 3`) -> platform `none`; known gaps: MS-DOS remains aspirational and has no build or packaging surface.
- `target.os_posix.abi_null.arch_riscv64` (`tier 3`) -> platform `platform.posix_min`; known gaps: RISC-V remains a future POSIX-min target with no bundle output today.
- `target.os_posix.abi_null.arch_x86_64` (`tier 3`) -> platform `platform.posix_min`; known gaps: POSIX minimal remains a portability floor, not a downloadable default bundle.
- `target.os_posix.abi_sdl.arch_x86_64` (`tier 3`) -> platform `platform.sdl_stub`; known gaps: SDL remains a declared adapter stub and is not part of the shipping mock release.
- `target.os_web.abi_wasm.arch_wasm32` (`tier 2`) -> platform `none`; known gaps: Web/WASM remains planned and does not ship in the current mock release.
- `target.os_win9x.abi_mingw.arch_x86_32` (`tier 3`) -> platform `platform.win9x`; known gaps: Windows 9x remains declared only and does not ship in the mock release.
- `target.os_winnt.abi_msvc.arch_x86_32` (`tier 2`) -> platform `platform.winnt`; known gaps: No Win32 x86 bundle is built in the current repository state.
