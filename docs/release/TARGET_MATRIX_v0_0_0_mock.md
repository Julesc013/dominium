Status: DERIVED
Last Reviewed: 2026-03-14
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: PLATFORM/DIST
Replacement Target: release-pinned target matrix and downloadable artifact availability model

# Target Matrix v0.0.0 Mock

Fingerprint: `1fda69af0918a7cb43fa8ff850ac3dd7319261710085e7d913e72fb10596dcd0`

## Axes

### CPU Architecture
- `arch.x86_32`
- `arch.x86_64`
- `arch.arm32`
- `arch.arm64`
- `arch.wasm32`
- `arch.wasm64`
- `arch.ppc32`
- `arch.ppc64`
- `arch.riscv64`

### OS Family
- `os.msdos`
- `os.win9x`
- `os.winnt`
- `os.linux`
- `os.macos_classic`
- `os.macosx`
- `os.bsd`
- `os.web`
- `os.posix`

### ABI / Runtime
- `abi.msvc`
- `abi.mingw`
- `abi.glibc`
- `abi.musl`
- `abi.cocoa`
- `abi.carbon`
- `abi.sdl`
- `abi.freestanding`
- `abi.wasm`
- `abi.null`

## Support Tiers

| Target | Tier | Platform Family | Built Now | Default Release Index | Supported Products | Default Install Profiles |
| --- | --- | --- | --- | --- | --- | --- |
| `target.os_bsd.abi_null.arch_x86_64` | `3` | `none` | `no` | `no` | `engine, server, setup` | `install.profile.server, install.profile.tools` |
| `target.os_linux.abi_glibc.arch_arm64` | `2` | `platform.linux_gtk` | `no` | `no` | `client, engine, game, launcher, server, setup` | `install.profile.client, install.profile.full, install.profile.server, install.profile.tools` |
| `target.os_linux.abi_glibc.arch_x86_64` | `1` | `platform.linux_gtk` | `no` | `no` | `client, engine, game, launcher, server, setup` | `install.profile.client, install.profile.full, install.profile.server, install.profile.tools` |
| `target.os_macos_classic.abi_carbon.arch_ppc32` | `3` | `platform.macos_classic` | `no` | `no` | `engine, setup` | `install.profile.tools` |
| `target.os_macosx.abi_cocoa.arch_arm64` | `2` | `platform.macos_cocoa` | `no` | `no` | `client, engine, game, launcher, server, setup` | `install.profile.client, install.profile.full, install.profile.server, install.profile.tools` |
| `target.os_msdos.abi_freestanding.arch_x86_32` | `3` | `none` | `no` | `no` | `engine, setup` | `install.profile.tools` |
| `target.os_posix.abi_null.arch_riscv64` | `3` | `platform.posix_min` | `no` | `no` | `engine, server, setup` | `install.profile.server, install.profile.tools` |
| `target.os_posix.abi_null.arch_x86_64` | `3` | `platform.posix_min` | `no` | `no` | `engine, server, setup` | `install.profile.server, install.profile.tools` |
| `target.os_posix.abi_sdl.arch_x86_64` | `3` | `platform.sdl_stub` | `no` | `no` | `client, game, launcher, setup` | `install.profile.client, install.profile.tools` |
| `target.os_web.abi_wasm.arch_wasm32` | `2` | `none` | `no` | `no` | `client, engine, setup` | `install.profile.client, install.profile.tools` |
| `target.os_win9x.abi_mingw.arch_x86_32` | `3` | `platform.win9x` | `no` | `no` | `engine, launcher, server, setup` | `install.profile.server, install.profile.tools` |
| `target.os_winnt.abi_msvc.arch_x86_32` | `2` | `platform.winnt` | `no` | `no` | `client, engine, game, launcher, server, setup` | `install.profile.client, install.profile.full, install.profile.server, install.profile.tools` |
| `target.os_winnt.abi_msvc.arch_x86_64` | `1` | `platform.winnt` | `yes` | `yes` | `client, engine, game, launcher, server, setup` | `install.profile.client, install.profile.full, install.profile.server, install.profile.tools` |

## Tier Policy

- Tier 1 targets are official only when they are actually built and pass convergence, clean-room, and platform-matrix gates.
- Tier 2 targets are experimental/planned and may ship CLI/TUI-only or with reduced renderer coverage.
- Tier 3 targets are declared/future only and must never appear in the default downloadable release index.
