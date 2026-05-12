# Input Backend Matrix

Status: PROVISIONAL

Phase: CONVERGE-11

Machine-readable source: `contracts/release/component_matrix.contract.toml`

## Backend Rows

| Backend | Status | Tier | Notes |
| --- | --- | --- | --- |
| keyboard_mouse | provisional | T0 | Client input binding source exists; command routing remains AppShell/runtime-owned. |
| raw_input | planned | T1 | Windows raw input lane. |
| ime | planned | T2 | Text composition lane. |
| gamepad | planned | T2 | Controller lane. |
| touch | research | T5 | Mobile/touch research lane. |
| accessibility_input | planned | T2 | Accessibility input lane. |

## Rule

Input events become commands through AppShell/runtime contracts. Input backends must not mutate truth directly.
