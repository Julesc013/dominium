Status: DERIVED
Last Reviewed: 2026-05-21
Supersedes: prior C90/C++98 language policy
Superseded By: none
Stability: provisional
Future Series: LANGUAGE-BASELINE, PORTABILITY-MATRIX
Replacement Target: `contracts/build/language_baseline.contract.toml`

# Dominium Language Policy

This document summarizes active language/toolchain constraints. The
machine-readable contract is `contracts/build/language_baseline.contract.toml`.
Determinism behavior remains governed by `docs/reference/specs/SPEC_DETERMINISM.md`
and `docs/governance/policies/DETERMINISM_REGRESSION_RULES.md`.

## 1. C17 Rules

Applies to C code, public C-compatible ABI surfaces, deterministic substrate,
packets, fixed-point math, save/replay encoders, and C-callable facades.

Build contract:

- Must compile as C17 (`CMAKE_C_STANDARD 17`, extensions off).
- Do not rely on C17 atomics, threads, or complex numbers as the portable
  cross-platform concurrency substrate.
- Stable ABI-facing structs must be POD-oriented, versioned where needed, and
  must not be raw save/network/replay formats.

## 2. C++17 Rules

Applies to implementation layers such as game, runtime services, renderer and
platform backends, apps, diagnostics, and compiled tooling.

Rules:

- Must compile as C++17 (`CMAKE_CXX_STANDARD 17`, extensions off).
- No C++ classes, templates, STL containers, exceptions, RTTI, allocator
  objects, or overload-only symbols may cross stable public C ABI.
- macOS 10.9.5 support forbids required use of `std::filesystem`, `std::pmr`,
  `std::to_chars`, `std::from_chars`, and `std::any`.
- Throwing `std::optional` and `std::variant` access paths require review and
  guards; prefer explicit result handling.

## 3. Boundary Rule

Deterministic simulation code must not depend on platform/system/render/UI code
as an input to simulation decisions. Platform and rendering layers may exist to
host the runtime loop and display derived state, but they must not mutate or
influence authoritative simulation state outside of the intent/delta contracts.

## 4. Retired Baseline

C89/C++98 is retired from active mainline governance. Historical and retro lanes
may remain archived or explicitly marked as future research, but they do not
govern default configure/build/test presets.
