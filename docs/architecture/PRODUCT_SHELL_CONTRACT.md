# Product Shell Contract (SHELL0)

Status: binding.
Scope: setup, launcher, client (out-of-game), client (in-game baseline), server, tools.

This contract defines what "done and working well" means for the product shell.
It defines responsibilities and acceptance criteria only. It does not add features.

Canonical anchors:
- `docs/architecture/PROCESS_ONLY_MUTATION.md`
- `docs/architecture/REFUSAL_SEMANTICS.md`
- `docs/architecture/SEMANTIC_STABILITY_POLICY.md`
- `docs/architecture/COMPATIBILITY_MODEL.md` (OPS1)
- `docs/architecture/OPS_TRANSACTION_MODEL.md` (OPS0)
- `docs/distribution/LAUNCHER_SETUP_CONTRACT.md`
- `docs/architecture/INSTALLER_CONTRACT.md`
- `docs/architecture/GUI_BASELINE.md`

Global rules (apply to all sections):
- CLI is canonical. TUI/GUI are projections of CLI semantics.
- Refusals are first-class, visible, and use canonical refusal codes.
- UI and tools are non-authoritative by default; any mutation must be a Process.
- Missing content is explained, never hidden.

## A) Setup

### Responsibilities (MUST)
- Install binaries into an install root and create a data root.
- Operate without network access for offline installs.
- Emit an ops log entry for install, uninstall, repair, and rollback.
- Never assume packs or content are present.
- Always explain outcomes (ok, refused, failed) with a human summary and refusal payloads.

### Prohibitions (MUST NOT)
- MUST NOT install content by default.
- MUST NOT mutate installed binaries after install.
- MUST NOT mutate an existing install silently.
- MUST NOT delete user data without explicit confirmation.

### Success criteria
Minimal install (code-only):
- Installs binaries and creates a data root.
- Launcher enumerates the install and instance manifests.
- Client reaches main menu with zero packs (refusals allowed).
- Server starts headless with an empty data root.

Maximal install (official bundle):
- Includes the same binaries as minimal plus bundled packs.
- First run is playable without downloads.
- Behavior does not branch on "minimal vs maximal" beyond detecting files present.

Offline install:
- Succeeds with all network access disabled.
- If network access is explicitly requested and unavailable, the outcome is a refusal.

Uninstall:
- Removes binaries and install-scoped artifacts.
- Preserves data root by default; deletion requires explicit, scoped confirmation.
- Explains exactly what was removed and what remains.

Repair:
- Verifies install manifest and restores missing or corrupted binaries.
- Does not rewrite packs or user data unless explicitly requested.
- Emits a repair ops log entry and summary.

Rollback:
- Restores the previous installed version using the ops log.
- Leaves current data root intact unless an explicit data rollback is requested.
- Emits a rollback ops log entry and summary.

Explicit setup statements:
- Setup never assumes content.
- Setup never mutates installs silently.
- Setup always explains outcomes.

## B) Launcher

### Responsibilities (MUST)
- Show installs, instances, and profiles in every UI surface.
- Surface missing packs, compatibility mode, and refusal details.
- Run mandatory preflight checks before launch or load:
  - install/instance manifest validation
  - capability lockfile validation
  - compat_report generation (OPS1)
  - sandbox policy and integrity checks
- Generate a compat_report for every load/join/run/update/migrate.
- Require explicit user confirmation before:
  - deleting or migrating instances
  - entering degraded/frozen/inspect-only modes
  - applying updates or rollbacks
  - connecting to network services

### Prohibitions (MUST NOT)
- MUST NOT hide missing content or refusal causes.
- MUST NOT proceed without a compat_report.
- MUST NOT mutate packs or installs without an explicit ops transaction.

### The 60-second rule (required)
- A new user can be shown how to use the launcher in under 60 seconds.
- The first-run guidance MUST fit on a single screen and be <= 120 words.
- It MUST name the three primitives: install, instance, profile, and the "Launch" action.

## C) Client (Out of Game)

### Responsibilities (MUST)
- Boot with zero assets and zero packs.
- Provide a loading/splash screen that reports:
  - build and version identifiers
  - pack discovery status
  - compatibility mode (full/degraded/frozen/inspect-only/refuse)
- Show a main menu with New World, Load World, Inspect Replay, Tools, Settings, Exit.
- Support CLI/TUI/GUI parity for every out-of-game action.
- Make debug and inspect modes discoverable (menu entry or documented CLI flag).

### Prohibitions (MUST NOT)
- MUST NOT require packs to reach the main menu.
- MUST NOT hide refusals or substitute silent fallbacks.
- MUST NOT provide GUI-only or TUI-only actions.

## D) Client (In Game - Baseline Only)

Baseline expectations (MUST exist):
- Camera exists and can be moved.
- Player movement exists (within lawful boundaries).
- HUD exists (minimal status and context).
- Pause menu exists and is accessible.
- Inspect mode exists and is read-only.
- Exit is always possible.

Explicit exclusions (MUST NOT be required):
- Activities, progression, economy, or objectives.
- Pack-specific assets, textures, or scripted scenarios.

## E) Server

### Responsibilities (MUST)
- Run headless-first (no UI required).
- Emit logs to the data root with timestamps and build identifiers.
- Generate a replay or event log for any authoritative run.
- Emit refusal payloads for invalid or incompatible runs.
- Persist crash markers and preserve logs on abnormal exit.

### Prohibitions (MUST NOT)
- MUST NOT require a renderer or UI to start.
- MUST NOT start without logging enabled.
- MUST NOT continue after a critical integrity refusal.

### Crash behavior
- On crash, exit with non-zero status and write a crash marker.
- On next start, surface the prior crash and offer recovery guidance.

### Overnight-run expectations
- Stable headless execution for an overnight duration (>= 8 hours).
- Deterministic output for identical inputs.
- Log rotation or bounded log growth.

## F) Tools

### Required tools (MUST exist by capability)
- Pack validation and schema checks.
- Capability inspection and compatibility reporting.
- Replay inspection and replay diffing.
- Refusal explanation tooling.
- Bugreport bundle creation and inspection.

### Read-only by default (MUST)
- Tools are read-only unless an explicit write flag is provided.
- Any mutation path must be a Process with refusal semantics.

### Inspection guarantees (MUST)
- Tools operate offline and on partial data.
- Outputs are deterministic and machine-readable (JSON or equivalent).
- Tools surface compat_report and refusal payloads without hiding details.

### Replay tooling guarantees (MUST)
- Inspect, validate, and diff replays without mutation.
- Export replay metadata for diagnostics and bugreports.

## Behavior matrix (sentinel, do not edit without TestX updates)

- ALLOW: PS-SETUP-MINIMAL - Minimal install succeeds.
- ALLOW: PS-SETUP-OFFLINE - Offline install succeeds.
- ALLOW: PS-SETUP-ROLLBACK - Rollback is explicit and logged.
- ALLOW: PS-LAUNCHER-PREFLIGHT - Preflight checks run before launch.
- ALLOW: PS-LAUNCHER-COMPAT-REPORT - compat_report is mandatory.
- ALLOW: PS-CLIENT-ZERO-ASSET - Zero-asset boot works.
- ALLOW: PS-CLIENT-PARITY - CLI/TUI/GUI parity for out-of-game actions.
- ALLOW: PS-SERVER-HEADLESS - Server runs headless-first.
- ALLOW: PS-TOOLS-READONLY - Tools default to read-only.
- ALLOW: PS-TOOLS-REPLAY - Replay inspection and diffing exist.
- FORBID: PS-SETUP-AUTO-CONTENT - Setup auto-installs content.
- FORBID: PS-SETUP-SILENT-MUTATION - Setup mutates installs silently.
- FORBID: PS-SETUP-ASSUME-CONTENT - Setup assumes any pack is present.
- FORBID: PS-LAUNCHER-HIDE-REFUSALS - Launcher hides refusal causes.
- FORBID: PS-LAUNCHER-BYPASS-COMPAT - Launcher proceeds without compat_report.
- FORBID: PS-CLIENT-REQUIRE-PACKS - Client requires packs for main menu.
- FORBID: PS-CLIENT-UI-ONLY - UI-only actions not present in CLI.
- FORBID: PS-SERVER-NO-LOGS - Server starts without logging.
- FORBID: PS-TOOLS-MUTATE-DEFAULT - Tools mutate state by default.
- FORBID: PS-TOOLS-BYPASS-LAW - Tools bypass law/refusal gates.

## Sentinel tags (do not remove)
- SHELL-PARITY-CLI-CANON

