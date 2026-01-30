# Launcher Walkthrough (UX-LAUNCH)

Status: evolving.
Scope: launcher UX walkthrough for CLI/TUI/GUI parity.

## 60-second walkthrough
1. Pick an **install** (binaries, read-only).
2. Pick or create an **instance** (data root).
3. Pick a **profile** (casual/hardcore/creator/server).
4. Run **Preflight** and confirm the result.
5. Launch in an explicit run mode.

This is a single-screen flow. It must name install, instance, profile, and launch.

## What every surface shows
- Install and instance visibility (counts and discoverability).
- Profile availability.
- Compatibility mode from compat_report.
- Missing packs and refusal details.

## Preflight outcome language
- FULL: all requirements satisfied.
- DEGRADED: optional content missing; confirmation required.
- FROZEN: authoritative execution halted; inspect/replay only.
- INSPECT-ONLY: read-only; no simulation mutation.
- REFUSE: blocked with refusal details.

## Discoverable diagnostics
Every surface exposes:
- logs path
- replays path
- bugreports path
- instance data path

In TUI/GUI this lives in Settings; in CLI use `launcher paths`.

## Run mode descriptions
- Play: client + local server
- Client only: remote server
- Server only: headless
- Inspect: read-only
- Replay: read-only replay

## Parity rule
CLI is canonical. TUI/GUI wrap CLI semantics and show the same outcomes.
