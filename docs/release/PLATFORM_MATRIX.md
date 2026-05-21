Status: DERIVED
Last Reviewed: 2026-05-21
Supersedes: none
Superseded By: none

# Platform Matrix

Status: PROVISIONAL

Phase: CONVERGE-11

Machine-readable source: `contracts/release/component_matrix.contract.toml`

## Purpose

The platform matrix records host/platform backend status. It separates OS families, platform IDs, backend switches, and support claims. Release-facing backend IDs are families; current CMake names may remain aliases until runtime naming is reviewed explicitly.

## Backend Status

| Backend | Status | Tier | Phase | Evidence / Notes |
| --- | --- | --- | --- | --- |
| null | available | T0 | base | `DOM_PLATFORM` accepts `null`; used for verification/headless lanes. |
| posix | available | T0 | base | POSIX headless/server substrate; current CMake alias is `posix_headless`. |
| win32 | provisional | T1 | desktop | Windows 7 SP1+ native platform family; CMake accepts `win32` and `win32_headless`. |
| cocoa | stub | T1 | desktop | Mac OS X 10.9.5+ native platform family; CMake accepts `cocoa`; current support is stub/headless-safe. |
| x11 | stub | T1 | desktop | First Linux desktop window lane; current CMake alias is `posix_x11`; support is not claimed implemented. |
| wayland | stub | T1 | desktop | Later Linux desktop window lane; current CMake alias is `posix_wayland`; support is not claimed implemented. |
| sdl | experimental | T1 | desktop | Dev/convenience adapter, not product identity; current CMake alias is `sdl2`. |

## Research And Later Platform Families

| Lane | Status | Tier | Phase | Evidence / Notes |
| --- | --- | --- | --- | --- |
| android | research | T5 | mobile | Deferred mobile lane, not first-wave desktop architecture. |

## OS Family Versus Backend

OS family names such as `winnt`, `macosx`, and `linux` identify target families. Platform backends such as `win32`, `cocoa`, `x11`, `wayland`, and `sdl` identify host adapter choices.

The null/headless baseline is a correctness lane. Desktop backends require toolchain, preset, smoke test, and package evidence before support can be claimed.

## Rules

Platform code may provide process lifecycle, filesystem access, time, threading, input events, IPC, windowing, and environment discovery.

Platform code must not own simulation truth, product behavior, domain law, or renderer semantics.
