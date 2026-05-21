Status: DERIVED
Last Reviewed: 2026-05-21
Supersedes: none
Superseded By: none

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

| Shell | Status | Tier | Phase | Products | Notes |
| --- | --- | --- | --- | --- | --- |
| win32 | stub | T1 | desktop | setup, launcher, client, server | Windows 7 SP1+ baseline native shell. Win32 source/stub surfaces exist; support requires smoke/package evidence. |
| appkit | planned | T1 | desktop | setup, launcher, tools | Mac OS X 10.9.5+ baseline native shell lane. |
| gtk | planned | T1 | desktop | setup, launcher, tools | First Linux native GUI lane. |
| qt | research | T2 | older | tools | Optional tools lane, not first-wave product identity. |
| winforms | research | T2 | older | launcher, tools | Convenience/admin/tools lane only. |
| swiftui | research | T4 | advanced | launcher, tools | Later modern macOS layer/bridge research. |
| winui | research | T4 | advanced | launcher, tools | Later modern Windows layer research; current alias `winui3` is not baseline. |

## Rules

Native GUI shells own layout and interaction affordances, not product semantics.

All native shell actions must project shared command, refusal, capability, event, and diagnostic surfaces.

Native shell status does not change product IDs, executable names, AppShell mode resolution, or packaging identity.
