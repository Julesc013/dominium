# Runtime Manifest

Status: PROVISIONAL
Phase: CONVERGE-07

CONVERGE-07 converged safe runtime-facing roots under `runtime/` and left mixed roots under review. This manifest records path movement only; it is not a semantic audit of every runtime file.

| Previous Root | New Location | Action | Notes |
| --- | --- | --- | --- |
| `appshell/` | `runtime/appshell/` | moved | AppShell bootstrap, commands, virtual paths, IPC, logging, supervisor, TUI, rendered stub, and mode-selection source moved intact. |
| `app/` | `runtime/app/` | moved | Shared C app-runtime library moved intact; target names, public include names, and aliases are unchanged. |
| `ui/` | `runtime/ui/` | moved | Shared UI model source moved intact. |
| `diag/` | `runtime/diagnostics/` | moved | Deterministic repro bundle helper moved intact. |
| `diagnostics/` | `runtime/diagnostics/` | already absent | No root-level `diagnostics/` source root existed during CONVERGE-07. |
| `input/` | `runtime/input/` | already absent | No root-level `input/` source root existed during CONVERGE-07. |
| `audio/` | `runtime/audio/` | already absent | No root-level `audio/` source root existed during CONVERGE-07. |
| `network/` | `runtime/network/` | already absent | No root-level `network/` source root existed during CONVERGE-07. |
| `storage/` | `runtime/storage/` | already absent | No root-level `storage/` source root existed during CONVERGE-07. |
| `platform/` | `runtime/platform/` | already absent | No root-level `platform/` source root existed during CONVERGE-07. |
| `render/` | `runtime/render/` | already absent | No root-level `render/` source root existed during CONVERGE-07. |
| `net/` | review | not moved | Mixed transport, anti-cheat, SRZ, testing, and server-authoritative policy code; do not move wholesale. |
| `control/` | review | not moved | Mixed process/control substrate; process-only mutation boundaries require deeper review. |
| `core/` | review | not moved | Mixed core/runtime/domain-adjacent substrate; do not move wholesale. |

## Current Runtime Source

- `runtime/app/`
- `runtime/appshell/`
- `runtime/diagnostics/`
- `runtime/ui/`
- `runtime/process_spawn.py`

No product roots, domain roots, content/data roots, generated roots, or contract/schema roots were moved in CONVERGE-07.

## References Updated

- Python imports now use `runtime.appshell`, `runtime.ui`, and `runtime.diagnostics`.
- The root CMake build now adds `runtime/app`.
- Active tooling and tests that referenced moved runtime source paths now point at the runtime subroots.

Historical docs may still mention old root paths as history. Broader stale-doc cleanup remains CONVERGE-12.
