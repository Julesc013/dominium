Status: DERIVED
Last Reviewed: 2026-02-01
Supersedes: none
Superseded By: none

--------------------------------
OWNERSHIP & RESPONSIBILITY
--------------------------------
ENGINE:
- None. This spec is implemented under `launcher/`.

GAME:
- None. This spec is implemented under `launcher/`.

TOOLS:
- None. Tools may only consume public APIs if needed.

SCHEMA:
- None (no canonical schema formats defined here).

FORBIDDEN:
- No launcher/setup orchestration logic in engine or game.
- No engine internal headers exposed outside engine targets.
- No game rules or policy implemented inside engine primitives.

DEPENDENCIES:
- Engine -> libs/ and schema/ only (never game/launcher/setup/tools).
- Game -> engine public API and schema/ only.
- Tools -> engine public API, game public API, and schema/ only.
- Launcher/Setup (if applicable) -> libs/contracts + schema (launcher may also use engine public API).
--------------------------------
# SPEC_LAUNCHER_PRELAUNCH_CONFIG — Pre-Launch Configuration, Safe Mode, and Recovery (Authoritative)

This spec defines the launcher pre-launch layer: how an instance’s effective launch configuration is resolved deterministically without mutating the instance manifest, how safe mode guarantees a runnable path, and how failures are tracked to support recovery without reinstalling.

Constraints (reasserted):
- Launcher core remains platform-agnostic; no OS/UI/renderer headers in core.
- C++98 only.
- All persistence is TLV (versioned, skip-unknown, forward-compatible).
- Deterministic resolution and refusal reasons for the same explicit inputs.
- No in-place mutation of live instances (staging + atomic swap only).
- All actions emit audit records (reason strings; no audit schema changes).

## 1. Configuration layering model (deterministic)

Inputs (in order of application):
1. **Locked instance manifest** (`manifest.tlv`): authoritative content graph + state markers; never mutated by overrides.
2. **Profile constraints** (optional): restrict allowed backends deterministically (e.g., `gfx` allowed list).
3. **Persisted instance overrides** (`config/config.tlv`): stable user preferences stored separately from the manifest.
4. **Ephemeral user overrides** (CLI/UI): provided per launch attempt; never persisted unless an explicit save action occurs in a higher layer.
5. **Safe mode overlay** (when selected): forces conservative settings and disables mods/packs without persisting.

Resolution rules:
- Later layers override earlier layers field-by-field.
- Resolution produces a canonical **resolved config** and an **effective manifest copy**:
  - Resolved config: renderer/backend selection, window/audio/input settings, network/debug flags, domain overrides.
  - Effective manifest: a copy of the base manifest with safe-mode disables applied (`enabled=0` on `mod`/`pack` entries).
- A stable `config_hash64 = FNV-1a64(canonical_resolved_config_tlv_bytes)` is computed for audit and failure tracking.

## 2. Persisted overrides (`config/config.tlv`)

Persistence rules:
- Stored under the instance root; never inside `manifest.tlv`.
- TLV schema is versioned and skip-unknown; unknown records are preserved.
- Storing config does not mutate any other instance file.

Relevant knobs (non-exhaustive):
- `gfx_backend`, `renderer_api`
- window mode/size/DPI/monitor
- audio device id, input backend
- `allow_network`, `debug_flags`
- domain overrides (key + enabled)
- auto-recovery tuning (`auto_recovery_failure_threshold`, `launch_history_max_entries`)

## 3. Safe mode (guaranteed recovery launch path)

Safe mode guarantees (effective behavior for a launch attempt):
- All mods disabled (`type=mod` entries become `enabled=0` in the effective manifest).
- All packs disabled (`type=pack` entries become `enabled=0` in the effective manifest).
- Minimal graphics selection: prefer `gfx_backend=null`; profile constraints may force a deterministic fallback (e.g., `soft`).
- No network access by default (`allow_network=0`) unless explicitly allowed for that safe-mode attempt.
- Base manifest selection prefers last-known-good snapshot when available (see 6).

Entry modes:
- Command-line flag (higher layers translate to a per-attempt safe mode override).
- UI action (higher layers translate to a per-attempt safe mode override).
- Automatic fallback after repeated failures (core may auto-enter safe mode for the next attempt; this is not an instance mutation).

Writeback rule:
- Safe mode never writes back to normal configs/state unless explicitly confirmed by the caller.

## 4. Failure tracking (`logs/launch_history.tlv`)

The launcher records the last N launch attempts per instance to support deterministic recovery suggestions.

Stored per instance at:
`<instance_root>/logs/launch_history.tlv`

Per-attempt fields (TLV, versioned, skip-unknown):
- timestamp (monotonic microseconds via injected time service)
- `manifest_hash64` (hash of the base manifest used for the attempt)
- `config_hash64` (hash of the resolved config)
- `safe_mode` (0/1)
- `outcome` (see 5)
- `exit_code` (for crash outcomes)
- `detail` (short string; optional)

## 5. Failure classification (deterministic)

Outcomes:
- `success`: the launched process/session completed successfully.
- `crash`: abnormal termination (non-zero exit, crash, etc.).
- `refusal`: prelaunch validation refused the attempt (incompatible configuration, permissions, sim-safety refusal, etc.).
- `missing_artifact`: a refusal specifically caused by missing required artifact payloads.

Classification rules:
- Validation failures produce refusal outcomes with explicit reason codes.
- If a refusal is due to missing artifacts, it is classified as `missing_artifact` for recovery policy.

## 6. Last-known-good (marking and rollback)

Known-good pointer:
- `known_good.tlv` points to a snapshot directory under `previous/` and stores:
  - instance id
  - previous dir name
  - snapshot manifest hash64
  - timestamp

Marking rules:
- Last-known-good is marked only after a successful launch attempt.
- Marking is implemented via the instance transaction engine:
  - snapshot is staged under `staging/known_good_snapshot/`
  - pointer `staging/known_good.tlv` is swapped atomically on commit

Rollback rules:
- Rollback restores the snapshot manifest and payload refs atomically via the same transaction engine.
- Rollback is never automatic; it must be an explicit user action.
- Rollback always emits an audit record describing the cause and source transaction id.

## 7. Prelaunch validation (deterministic; auditable)

Validation checks are performed on the effective manifest + resolved config:
- Required artifact payloads exist for enabled `engine`/`game`/`runtime` entries.
- Renderer/backend compatibility (supported backend name).
- Pack ecosystem simulation safety (enabled packs only).
- Logs directory is writable where required.

Validation failure requirements:
- Provide a clear refusal reason code and a recovery suggestion.
- Record validation results in audit (including all failures, in deterministic order).

## 8. Audit integration (per launch attempt)

Each launch attempt records (as audit reason strings):
- Effective resolved configuration (including hashes)
- Applied overrides (persisted + ephemeral + safe-mode derived)
- Safe mode status and whether it was auto-entered
- Validation results (ok or explicit failure list)
- Final outcome (success/crash/refusal/missing_artifact) and exit code
- Last-known-good writeback result (ok/skipped/fail) with safe-mode confirmation status