# Native App Matrix

Status: PROVISIONAL

Phase: CONVERGE-11

Machine-readable source: `contracts/release/component_matrix.contract.toml`

## Purpose

The native app matrix records shell strategy for setup, launcher, admin/tools, client host surfaces, and server operator surfaces. It does not implement native GUI code.

## Strategy

| Product | Strategy |
| --- | --- |
| setup | Prefer native shell where available; TUI and CLI remain deterministic fallbacks. |
| launcher | Prefer native shell where available; TUI and CLI expose the same preflight and refusal semantics. |
| client | Rendered-first; native host/window/platform surfaces do not own client behavior. |
| server | Headless/TUI-first; native GUI is not a baseline requirement. |
| tools | CLI/TUI first; native UI only when useful and explicitly classified as shipped product tooling. |

## Native Shell Rows

| Shell | Status | Tier | Products | Notes |
| --- | --- | --- | --- | --- |
| win32 | stub | T1 | setup, launcher, client, server | Win32 source/stub surfaces exist; support requires smoke/package evidence. |
| appkit | planned | T1 | setup, launcher, tools | macOS baseline native shell lane. |
| gtk | planned | T1 | setup, launcher, tools | Linux first native GUI lane. |
| qt | research | T2 | tools | Optional/research only. |
| winforms | research | T2 | launcher, tools | Convenience/admin/tools lane only. |
| swiftui | research | T4 | launcher, tools | Modern macOS layer/bridge research. |
| winui3 | research | T4 | launcher, tools | Modern Windows layer research. |

## Rules

Native GUI shells own layout and interaction affordances, not product semantics.

All native shell actions must project shared command, refusal, capability, event, and diagnostic surfaces.

Native shell status does not change product IDs, executable names, AppShell mode resolution, or packaging identity.
