Status: DERIVED
Last Reviewed: 2026-03-13
Stability: provisional
Future Series: APPSHELL
Replacement Target: release-pinned platform adapter contracts and install discovery guarantees

# Platform Formalize Final

Fingerprint: `ea0e7a7023a8efffceac1c527f2ec769da2a41db7cc5e09900a3daa9e5cd4e78`

## Supported Platforms

| Platform | Tier | Declared Native | Declared Rendered | Declared TUI | Declared CLI |
| --- | --- | --- | --- | --- | --- |
| `platform.win9x` | `subset` | `yes` | `no` | `yes` | `yes` |
| `platform.winnt` | `full` | `yes` | `yes` | `yes` | `yes` |
| `platform.macos_classic` | `subset` | `yes` | `no` | `no` | `yes` |
| `platform.macos_cocoa` | `full` | `yes` | `yes` | `yes` | `yes` |
| `platform.linux_gtk` | `full` | `yes` | `yes` | `yes` | `yes` |
| `platform.posix_min` | `subset` | `no` | `no` | `yes` | `yes` |
| `platform.sdl_stub` | `future_stub` | `no` | `yes` | `yes` | `yes` |

## Current Host Probe

| Product | Platform | Context | Supported Modes | Available Modes | Renderers | IPC |
| --- | --- | --- | --- | --- | --- | --- |
| `client` | `platform.winnt` | `tty` | `rendered`, `tui`, `cli` | `rendered`, `tui`, `cli` | `null`, `software`, `opengl` | `named_pipe` |
| `launcher` | `platform.winnt` | `tty` | `tui`, `cli` | `tui`, `cli` | `null`, `software`, `opengl` | `named_pipe` |
| `setup` | `platform.winnt` | `tty` | `tui`, `cli` | `tui`, `cli` | `null`, `software`, `opengl` | `named_pipe` |
| `server` | `platform.winnt` | `tty` | `tui`, `cli` | `tui`, `cli` | `null`, `software`, `opengl` | `named_pipe` |

## Deferred Platforms

- `platform.win9x` and `platform.macos_classic` remain subset targets with conservative capability declarations only.
- `platform.sdl_stub` is declared for future portable windowing but does not claim an active adapter in the repo today.
- DirectX, Vulkan, and Metal renderer capabilities remain declared `no` until concrete backends land.

## Readiness

- UI mode selection now depends on the canonical platform probe.
- CAP-NEG endpoint descriptors include platform id, platform descriptor hash, and computed capability ids.
- The platform matrix is ready for REPO-LAYOUT-0 virtual paths and INSTALL-DISCOVERY-0.
