# Platform Matrix

Status: PROVISIONAL

Phase: CONVERGE-11

Machine-readable source: `contracts/release/component_matrix.contract.toml`

## Purpose

The platform matrix records host/platform backend status. It separates OS families, platform IDs, backend switches, and support claims.

## Backend Status

| Backend | Status | Tier | Evidence / Notes |
| --- | --- | --- | --- |
| null | available | T0 | `DOM_PLATFORM` accepts `null`; used for verification/headless lanes. |
| posix_headless | available | T0 | CMake defaults to `posix_headless` on UNIX hosts. |
| win32 | provisional | T1 | CMake accepts `win32`; Windows presets and Win32 source surfaces exist. |
| win32_headless | provisional | T0 | CMake accepts `win32_headless`. |
| cocoa | stub | T1 | CMake accepts `cocoa`; current platform docs describe Cocoa as stub/headless-safe. |
| posix_x11 | stub | T1 | CMake accepts `posix_x11`; Linux desktop support is not claimed implemented. |
| posix_wayland | stub | T1 | CMake accepts `posix_wayland`; Linux desktop support is not claimed implemented. |
| sdl2 | experimental | T1 | `DOM_BACKEND_SDL2` and `DOM_FETCH_SDL2` exist; SDL2 is a dev/convenience adapter, not product identity. |
| android | research | T5 | Deferred mobile lane. |

## OS Family Versus Backend

OS family names such as `winnt`, `macosx`, and `linux` identify target families. Platform backends such as `win32`, `cocoa`, `posix_x11`, `posix_wayland`, and `sdl2` identify host adapter choices.

The null/headless baseline is a correctness lane. Desktop backends require toolchain, preset, smoke test, and package evidence before support can be claimed.

## Rules

Platform code may provide process lifecycle, filesystem access, time, threading, input events, IPC, windowing, and environment discovery.

Platform code must not own simulation truth, product behavior, domain law, or renderer semantics.
