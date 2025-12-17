# Dominium Launcher Architecture

Doc Version: 1

This document describes the launcher’s system architecture and the invariants that make it auditable, deterministic, offline-capable, and safe for simulation correctness.

## Goals (Non-Negotiable)

- Launcher must not affect simulation correctness.
- Launcher core is platform-agnostic and C++98-only.
- All persistence is versioned TLV with skip-unknown semantics.
- Deterministic behavior is required (no hidden OS-dependent ordering).
- Every run and operation emits audit records.
- Must function under `--ui=native`, `--ui=dgfx`, `--ui=null`, and `--gfx=null`.

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

See `docs/launcher/DIAGNOSTICS_AND_SUPPORT.md` and `docs/SPEC_LAUNCHER_CORE.md`.

## Data Formats and Migrations

All persisted state uses a versioned TLV root with a schema version tag and skip-unknown semantics. Older versions may be migrated to the current version; unsupported newer versions must be refused.

See:
- `docs/launcher/INSTANCE_MODEL.md`
- `docs/SPEC_CONTAINER_TLV.md`
- `docs/DATA_FORMATS.md`

## Related Documents

- `docs/launcher/INSTANCE_MODEL.md`
- `docs/launcher/ARTIFACT_STORE.md`
- `docs/launcher/PACK_SYSTEM.md`
- `docs/launcher/UI_SYSTEM.md`
- `docs/launcher/RECOVERY_AND_SAFE_MODE.md`
- `docs/launcher/DIAGNOSTICS_AND_SUPPORT.md`
- `docs/launcher/SECURITY_AND_TRUST.md`
- `docs/launcher/BUILD_AND_PACKAGING.md`

