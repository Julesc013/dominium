# Product Mode Matrix

Status: PROVISIONAL

Phase: CONVERGE-11

Machine-readable source: `contracts/release/component_matrix.contract.toml`

## Purpose

Product modes describe how product entrypoints bind AppShell/runtime surfaces. They do not move product code and do not change AppShell mode resolution.

## Matrix

| Product | Preferred Mode Order | Status | Notes |
| --- | --- | --- | --- |
| client | rendered -> tui -> cli | provisional | Rendered-first client; native host/window/input is platform support, not product semantics. |
| server | headless -> tui -> cli | provisional | Headless and non-interactive first; TUI/CLI are operator surfaces. |
| setup | os_native -> tui -> cli | provisional | Native shell preferred where available; CLI remains deterministic baseline. |
| launcher | os_native -> tui -> cli | provisional | Native shell preferred where available; CLI/TUI must expose the same refusals and preflight decisions. |
| tools | cli -> tui -> os_native | planned | Shipped tools require explicit classification; developer tools remain under `tools/`. |

## Modes

| Mode | Status | Rule |
| --- | --- | --- |
| cli | available | Canonical command and refusal surface. |
| tui | stub | Must project CLI semantics; stubs are not full support. |
| headless | available | No UI; must preserve deterministic command behavior. |
| rendered | provisional | Client presentation mode only. |
| os_native | stub | Native toolkit shell only; it must not own product behavior. |

## Rules

Product behavior must not live in GUI toolkit, renderer, platform, or package format code.

All product modes consume shared command, state, event, capability, refusal, and diagnostic surfaces.

Explicit unavailable mode selection must fail loudly or degrade through AppShell policy with structured diagnostics.
