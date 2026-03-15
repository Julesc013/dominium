Status: DERIVED
Last Reviewed: 2026-03-14
Stability: provisional
Future Series: PLATFORM/DIST
Replacement Target: release-pinned target matrix and downloadable artifact availability model

# ARCH-MATRIX Final

Fingerprint: `48bff142af66050d569f775d5c4bf2759afc91c1f40702e093b6b34aa0c2739f`

## Full Target Matrix Table

| Target | Tier | Built | Release Index Default | Required Capabilities | Known Missing Features |
| --- | --- | --- | --- | --- | --- |
| `target.os_bsd.abi_null.arch_x86_64` | `3` | `no` | `no` | `cap.renderer.null, cap.ui.cli` | `No BSD bundle or adapter lane is shipped in v0.0.0-mock.` |
| `target.os_linux.abi_glibc.arch_arm64` | `2` | `no` | `no` | `cap.ipc.local_socket, cap.renderer.null, cap.ui.cli, cap.ui.tui` | `No ARM64 Linux portable bundle is built in the current repository state.` |
| `target.os_linux.abi_glibc.arch_x86_64` | `1` | `no` | `no` | `cap.ipc.local_socket, cap.renderer.software, cap.ui.cli, cap.ui.tui` | `Linux x86_64 is Tier 1 only when a bundle is actually built and validated.` |
| `target.os_macos_classic.abi_carbon.arch_ppc32` | `3` | `no` | `no` | `cap.renderer.null, cap.ui.cli` | `Classic Mac remains declared only; no Carbon package or validation lane exists.` |
| `target.os_macosx.abi_cocoa.arch_arm64` | `2` | `no` | `no` | `cap.ipc.local_socket, cap.renderer.software, cap.ui.cli, cap.ui.tui` | `No macOS universal bundle is built in the current repository state.` |
| `target.os_msdos.abi_freestanding.arch_x86_32` | `3` | `no` | `no` | `cap.renderer.null, cap.ui.cli` | `MS-DOS remains aspirational and has no build or packaging surface.` |
| `target.os_posix.abi_null.arch_riscv64` | `3` | `no` | `no` | `cap.renderer.null, cap.ui.cli, cap.ui.tui` | `RISC-V remains a future POSIX-min target with no bundle output today.` |
| `target.os_posix.abi_null.arch_x86_64` | `3` | `no` | `no` | `cap.renderer.null, cap.ui.cli, cap.ui.tui` | `POSIX minimal remains a portability floor, not a downloadable default bundle.` |
| `target.os_posix.abi_sdl.arch_x86_64` | `3` | `no` | `no` | `cap.renderer.software, cap.ui.cli, cap.ui.rendered` | `SDL remains a declared adapter stub and is not part of the shipping mock release.` |
| `target.os_web.abi_wasm.arch_wasm32` | `2` | `no` | `no` | `cap.renderer.software, cap.ui.rendered` | `Web/WASM remains planned and does not ship in the current mock release.` |
| `target.os_win9x.abi_mingw.arch_x86_32` | `3` | `no` | `no` | `cap.renderer.null, cap.ui.cli, cap.ui.tui` | `Windows 9x remains declared only and does not ship in the mock release.` |
| `target.os_winnt.abi_msvc.arch_x86_32` | `2` | `no` | `no` | `cap.ipc.named_pipe, cap.renderer.software, cap.ui.cli, cap.ui.tui` | `No Win32 x86 bundle is built in the current repository state.` |
| `target.os_winnt.abi_msvc.arch_x86_64` | `1` | `yes` | `yes` | `cap.ipc.named_pipe, cap.renderer.software, cap.ui.cli, cap.ui.tui` | `OS-native UI remains optional; the guaranteed fallback chain is rendered/TUI/CLI.` |

## Tier Breakdown

- Tier 1: `2`
- Tier 2: `4`
- Tier 3: `7`

## Declared vs Built Targets

- Built `win64` -> `target.os_winnt.abi_msvc.arch_x86_64` (`tier 1`; source `dist`)

### Release Index Rows

- `dist/v0.0.0-mock/win64/dominium/manifests/release_index.json`
  - `os.winnt` / `arch.x86_64` / `abi.msvc` -> `target.os_winnt.abi_msvc.arch_x86_64` (`tier 1`)
- `build/tmp/archive_policy_dist/v0.0.0-mock/win64/dominium/manifests/release_index.json`
  - `os.winnt` / `arch.x86_64` / `abi.msvc` -> `target.os_winnt.abi_msvc.arch_x86_64` (`tier 1`)
- `build/tmp/governance_model_dist/v0.0.0-mock/win64/dominium/manifests/release_index.json`
  - `os.winnt` / `arch.x86_64` / `abi.msvc` -> `target.os_winnt.abi_msvc.arch_x86_64` (`tier 1`)
- `build/tmp/performance_envelope_dist/v0.0.0-mock/win64/dominium/manifests/release_index.json`
  - `os.winnt` / `arch.x86_64` / `abi.msvc` -> `target.os_winnt.abi_msvc.arch_x86_64` (`tier 1`)
- `build/tmp/performance_envelope_server_dist/v0.0.0-mock/win64/dominium/manifests/release_index.json`
  - `os.winnt` / `arch.x86_64` / `abi.msvc` -> `target.os_winnt.abi_msvc.arch_x86_64` (`tier 1`)
- `build/tmp/update_model_dist/v0.0.0-mock/win64/dominium/manifests/release_index.json`
  - `os.winnt` / `arch.x86_64` / `abi.msvc` -> `target.os_winnt.abi_msvc.arch_x86_64` (`tier 1`)
- `build/tmp/update_model_test_dist/v0.0.0-mock/win64/dominium/manifests/release_index.json`
  - `os.winnt` / `arch.x86_64` / `abi.msvc` -> `target.os_winnt.abi_msvc.arch_x86_64` (`tier 1`)

## Readiness

- `target.os_winnt.abi_msvc.arch_x86_64` -> convergence `complete`, clean-room `complete`, dist-4 `complete`, overall `complete`
- Endpoint descriptor target fields present: `official.abi_id`, `official.arch_id`, `official.os_id`, `official.target_id`, `official.target_tier`
- Readiness for TRUST-MODEL-0 and DIST-7 packaging: `ready`
