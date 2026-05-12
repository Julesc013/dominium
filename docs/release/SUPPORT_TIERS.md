# Support Tiers

Status: PROVISIONAL

Phase: CONVERGE-11

Machine-readable source: `contracts/release/component_matrix.contract.toml`

## Purpose

Support tiers classify how close a product, backend, shell, toolchain, or package lane is to release support. A tier is not a support claim by itself. A lane becomes supported only when the component matrix marks it with a support-capable status and the repo has the matching toolchain, preset, package path, smoke test, and release docs.

## Tiers

| Tier | Name | Purpose |
| --- | --- | --- |
| T0 | correctness_baseline | Deterministic, headless, portable baseline for tests, replay, and minimal operation. |
| T1 | early_modern_desktop | Initial public-ish desktop coverage on modern Windows, macOS, and Linux. |
| T2 | broad_compatibility | Wider compatibility coverage including older desktop paths where feasible. |
| T3 | retro_research | Legacy/retro lanes requiring frozen toolchains and smoke tests. |
| T4 | advanced_modern | Advanced GPU/render/platform/toolchain work after baseline stability. |
| T5 | mobile_web_exotic | Mobile, web, exotic OS, console, and special-device research lanes. |

## Support Rule

Rows with status `stub`, `planned`, `research`, `unknown`, `unsupported`, or `blocked` are not supported lanes. They are planning or refusal surfaces until evidence exists.

Support requires:

- explicit matrix status
- build or validation preset
- smoke test or verification gate
- package or install projection path
- release docs naming the actual lane

CONVERGE-11 records support posture only. It does not implement backends, native shells, renderers, packages, or toolchains.
