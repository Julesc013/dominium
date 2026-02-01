Status: DERIVED
Last Reviewed: 2026-02-01
Supersedes: none
Superseded By: none

# Debug and Diagnostics Model (DIAG0)

Status: binding.
Scope: logging, refusals, errors, replays, and bugreports across products.

This document defines diagnostics expectations only. It does not add features.

## Logging expectations
- Every product (setup, launcher, client, server, tools) MUST write logs.
- Logs MUST include:
  - build identifiers (version, build number)
  - runtime context (mode, data root, install/instance identifiers)
  - compatibility mode and any refusal codes
- Logs MUST be append-only and timestamped.
- Logs MUST be accessible without network access.

## Error vs refusal
Refusal:
- Expected, deterministic, and law-admitted.
- Uses canonical refusal codes and structured payloads.
- Does not mutate authoritative state.

Error:
- Unexpected failure or invariant violation.
- Must be logged with enough context for reproduction.
- May terminate the process with non-zero exit.

## Log access
- CLI exposes log locations and recent entries via deterministic output.
- TUI/GUI must provide a discoverable path to the same logs.
- Logs must be retrievable even when packs are missing (inspect-only is allowed).

## Replay generation and use
- Authoritative runs MUST emit replay or event logs.
- Replays are the default artifact for reproduction and regression analysis.
- Replay inspection MUST be available via read-only tools.

## Bugreport bundles (conceptual)
- Bugreports are immutable bundles per `docs/architecture/BUGREPORT_MODEL.md`.
- Creation is CLI-first; TUI/GUI wrappers call the same path.
- A bugreport SHOULD include:
  - replay bundle
  - compat_report
  - refusal summary
  - ops log excerpt
  - relevant logs

## Privacy and redaction
- Redaction may remove personal data but MUST NOT alter replays or saves.
- Redaction actions MUST be logged and summarized.