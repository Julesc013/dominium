# Dominium Launcher Architecture

Doc Version: 2

This document describes the launcher’s system architecture and the invariants that make it auditable, deterministic, offline-capable, and safe for simulation correctness.

## Goals (Non-Negotiable)

- Launcher must not affect simulation correctness.
- Launcher core is platform-agnostic and C++98-only.
- All persistence is versioned TLV with skip-unknown semantics.
- Deterministic behavior is required (no hidden OS-dependent ordering).
- Every run and operation emits audit records.
- Must function under `--ui=native`, `--ui=dgfx`, `--ui=null`, and `--gfx=null`.

## Launcher as Control Plane

The launcher is the **control plane** for the Dominium ecosystem:

- It owns **instance state**, **artifact store**, **pack selection**, and **tool launching**.
- It produces deterministic, machine-readable **run artifacts** (handshake, audit, selection summary, exit status).
- It must never change simulation correctness: the engine is the **data plane** that consumes the launcher’s resolved inputs.

Control-plane commands must be usable in automation and CI under `--ui=null --gfx=null`.

## Shared Core Libraries

Launcher core is built on the shared core libraries defined in
`docs/core/CORE_LIBRARIES.md` (TLV, err_t, logging, jobs, caps/solver, audit,
providers). Any new launcher kernel code must use these shared modules rather
than re-implementing equivalents.

## Installed-State Contract (Setup ↔ Launcher)

The launcher is a **consumer** of Setup Core’s installed-state file and never performs install logic.

Contract:
- The installed state lives at `<install_root>/.dsu/installed_state.tlv` (authoritative).
- Legacy state lives at `<install_root>/.dsu/installed_state.dsustate` and is imported on first run when needed.
- The launcher **refuses to run** when the state file is missing or invalid.
- On refusal, the launcher prints recovery guidance (verify/repair) and exits without attempting install.
- The installed state is the authoritative source for component enumeration and critical path validation.

Smoke validation:
- `dominium-launcher --smoke-test --state <install_root>/.dsu/installed_state.tlv`

Note: Setup produces `installed_state.tlv` with a shared core schema
(`docs/core/INSTALLED_STATE_CONTRACT.md`). The launcher parses the Setup state
via launcher core installed-state helpers and imports legacy
`.dsu/installed_state.dsustate` on demand.

## Layers

### 1) Launcher Core (Deterministic Foundation)

Responsibilities:
- Models: instance state, pack ecosystem, artifacts, prelaunch planning, recovery policy.
- Persistence: encode/decode versioned TLV; migrate older versions; refuse unsupported newer versions.
- Deterministic selection and validation: given explicit inputs and injected capabilities.
- Audit enrichment: records “selected-and-why” and refusal reasons.

Properties:
- No direct OS/UI/toolkit dependencies.
- No background services or daemons.
- No reliance on filesystem enumeration ordering.

### 2) Services Facade (Capability-Gated Adapters)

The core interacts with the outside world only through a versioned C ABI “services” facade (filesystem, time, process, optional networking/archive capability stubs). This keeps core logic platform-agnostic and testable.

### 3) Launcher Application Layer (Policy + UX)

Responsibilities:
- CLI parsing and user-facing commands.
- UI backend selection and rendering (native/dgfx/null).
- Process spawning and wiring launch parameters to the game.
- Packaging-facing entrypoints and sensible defaults for `--home`.

The application layer must not introduce simulation-affecting behavior; it only supplies inputs to the core and executes the core’s plan.

## Determinism Boundaries

Determinism is defined as: same explicit inputs + same verified artifacts + same selected backends ⇒ same core decisions and persisted outputs.

Key rules:
- All ordering is explicit (stable sorts or preserved list order).
- Time is only used when injected (monotonic “now_us”) and must be recorded in audit.
- Unknown TLV tags are skipped on read and preserved on re-encode where round-trip safety is required.

## Audit Model

Every run produces an audit record that includes:
- Inputs (argv / command parameters)
- Selected profile and chosen subsystem backends
- Deterministic “reasons” explaining decisions and refusals
- Build metadata (version string, build id, git hash, toolchain id)

Selection invariants:
- Selection visibility has a single source of truth: `selection_summary.tlv` (see `docs/launcher/ECOSYSTEM_INTEGRATION.md`).
- Per-run audit may embed `selection_summary.tlv` bytes; when embedded, the bytes must match the file written in the run directory.
- All refusals must be explicit and audited (no silent validation failures).

See `docs/launcher/DIAGNOSTICS_AND_SUPPORT.md` and `docs/SPEC_LAUNCHER_CORE.md`.

## Run Directories (Per Launch Attempt)

For every launch attempt (game or tool), including refusals, the launcher creates:

`<state_root>/instances/<instance_id>/logs/runs/<run_dir_id>/`

Where:
- `run_dir_id` is the 16-hex-digit `run_id` without the `0x` prefix.

Stable file set (best-effort writes; missing files must be explicit):
- `handshake.tlv` (launcher → engine/tool handshake)
- `launch_config.tlv` (resolved launch configuration snapshot for the attempt)
- `selection_summary.tlv` (unified selection summary snapshot)
- `exit_status.tlv` (exit code, termination type, timestamps, capture support flags)
- `audit_ref.tlv` (per-run audit record; references handshake/selection paths; may embed selection summary bytes)
- `stdout.txt` / `stderr.txt` when capture is supported; otherwise the files may be absent and `exit_status.tlv` must indicate capture support explicitly.

Retention policy (enforced best-effort after each attempt):
- Keep the last `N` run directories per instance (default `N=8`).
- `N` is configurable for control-plane launches via `--keep_last_runs=<N>`; `N=0` disables cleanup.
- Never delete the most recent failed run automatically (failure heuristic: run audit missing/unreadable, or `audit.exit_result != 0`).

## Diagnostics Bundle (Control Plane)

The control plane can export a deterministic diagnostics bundle directory:
- `diag-bundle <instance_id> --out=<dir>`

Invariants:
- The bundle contains a full instance export.
- When a last run exists, the bundle copies last-run artifacts to `out/last_run/<run_dir_id>/`:
  - `handshake.tlv`, `launch_config.tlv`, `selection_summary.tlv`, `exit_status.tlv`, `audit_ref.tlv`
- The bundle writes `out/last_run_selection_summary.txt` (stable, line-oriented dump).

## Data Formats and Migrations

All persisted state uses a versioned TLV root with a schema version tag and skip-unknown semantics. Older versions may be migrated to the current version; unsupported newer versions must be refused.

See:
- `docs/launcher/INSTANCE_MODEL.md`
- `docs/SPEC_CONTAINER_TLV.md`
- `docs/DATA_FORMATS.md`

## Related Documents

- `docs/launcher/INSTALLED_STATE_CONTRACT.md`
- `docs/launcher/INSTANCE_MODEL.md`
- `docs/launcher/ARTIFACT_STORE.md`
- `docs/launcher/PACK_SYSTEM.md`
- `docs/launcher/UI_SYSTEM.md`
- `docs/launcher/RECOVERY_AND_SAFE_MODE.md`
- `docs/launcher/DIAGNOSTICS_AND_SUPPORT.md`
- `docs/launcher/SECURITY_AND_TRUST.md`
- `docs/launcher/BUILD_AND_PACKAGING.md`
- `docs/launcher/CLI.md`
- `docs/launcher/ECOSYSTEM_INTEGRATION.md`
- `docs/launcher/TESTING.md`
