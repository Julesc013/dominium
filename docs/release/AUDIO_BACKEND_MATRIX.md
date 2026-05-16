Status: DERIVED
Last Reviewed: 2026-05-16
Supersedes: none
Superseded By: none

# Audio Backend Matrix

Status: PROVISIONAL

Phase: CONVERGE-11

Machine-readable source: `contracts/release/component_matrix.contract.toml`

## Backend Rows

| Backend | Status | Tier | Notes |
| --- | --- | --- | --- |
| null | planned | T0 | Silent/correctness lane; no implemented support claimed. |
| wasapi | planned | T1 | Windows audio lane. |
| directsound | research | T3 | Legacy Windows research lane. |
| coreaudio | planned | T1 | macOS audio lane. |
| alsa | planned | T1 | Linux audio lane. |
| pulseaudio | planned | T2 | Linux desktop lane. |
| pipewire | planned | T2 | Modern Linux desktop lane. |
| sdl_audio | research | T2 | SDL convenience adapter, not product identity. |

## Rule

Audio is a runtime backend. It must not own simulation truth, domain logic, product behavior, or deterministic authority.
