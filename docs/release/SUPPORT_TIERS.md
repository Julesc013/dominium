Status: DERIVED
Last Reviewed: 2026-05-21
Supersedes: none
Superseded By: none

# Support Tiers

Status: PROVISIONAL

Phase: CONVERGE-11

Machine-readable source: `contracts/release/component_matrix.contract.toml`

## Purpose

Support tiers classify how close a product, backend, shell, toolchain, or package lane is to release support. A tier is not a support claim by itself. Phase, status, and evidence are separate fields; era labels such as "modern" or "retro" are not renderer or platform identities. A lane becomes supported only when the component matrix marks it with a support-capable status and the repo has the matching toolchain, preset, package path, smoke test, and release docs.

## Tiers

| Tier | Name | Phase | Purpose |
| --- | --- | --- | --- |
| T0 | base | base | Deterministic, headless, portable baseline for tests, replay, and minimal operation. |
| T1 | desktop | desktop | Primary desktop coverage for Windows 7 SP1+, Mac OS X 10.9.5+, and supported practical Linux toolchains. |
| T2 | secondary | older | Secondary compatibility or tooling lanes that do not define first-wave architecture. |
| T3 | backport_research | older | Legacy, retro, or back-port lanes requiring frozen toolchains, smoke tests, and explicit review. |
| T4 | advanced | advanced | Advanced GPU/render/platform/toolchain work after baseline stability. |
| T5 | mobile_web_exotic | mobile | Mobile, web, exotic OS, console, and special-device research lanes. |

## Support Rule

Rows with status `stub`, `planned`, `research`, `unknown`, `unsupported`, or `blocked` are not supported lanes. They are planning or refusal surfaces until evidence exists.

Support requires:

- explicit matrix status
- build or validation preset
- smoke test or verification gate
- package or install projection path
- release docs naming the actual lane

CONVERGE-11 records support posture only. It does not implement backends, native shells, renderers, packages, or toolchains.
