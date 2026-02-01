Status: DERIVED
Last Reviewed: 2026-02-01
Supersedes: none
Superseded By: none

# Product Boundaries

This document summarizes the responsibilities and non-overlap between products.

## Client
- User-facing runtime entrypoint (UI + interaction orchestration)
- Uses platform runtime + renderer interfaces; no OS calls above platform layer
- CLI-only modes are supported; renderer is optional in smoke paths
- No authoritative simulation decisions (engine/game remain authoritative)

## Server
- Headless authoritative runtime shell
- No windowing, GPU, or audio requirements
- Deterministic CLI-only smoke/status for tests

## Launcher
- Orchestrates installed products and profiles
- Performs capability probing and launch handshakes
- No embedded content; best-effort discovery only

## Setup
- Offline bootstrap and directory preparation
- Validates prerequisites (best-effort)
- No content installed by default

## Tools
- CLI-first inspection/validation/replay utilities
- Read-only by default; explicit write/elevation required if added later
- No embedded content