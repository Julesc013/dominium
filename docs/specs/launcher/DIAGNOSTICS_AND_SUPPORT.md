Status: DERIVED
Last Reviewed: 2026-02-01
Supersedes: none
Superseded By: none

# Diagnostics and Support

Doc Version: 1

This document describes what diagnostic data the launcher produces, how it is structured, and how to collect it for support or regression analysis.

## Audit Logs

Every run emits an audit log containing:
- explicit inputs (argv and user-chosen parameters)
- selected profile and backend selections (and why)
- refusal reasons and validation failures
- build metadata (version/build id/git hash/toolchain id)

Audit output is versioned TLV and intended to be machine-readable. A text representation may also be produced for human inspection.

See `docs/specs/SPEC_LAUNCHER_CORE.md`.

## Per-Instance Logs

Instances keep:
- `logs/launch_history.tlv` for outcomes and recovery decisions
- any additional logs produced by pack prelaunch tasks (when applicable)

## Support Bundle (Crash Bundle)

The launcher can generate a deterministic “support bundle” for inspection. A bundle should include:
- the most recent audit record(s)
- the instance manifest and config
- launch history and last-known-good pointer (if present)
- a minimal build-info summary (version/build id/git hash/toolchain id)

The bundle must be deterministic (stable ordering and timestamps) and must not require network access.

### Generating a Bundle

For CI and developer workflows, the repository includes a deterministic bundle generator:

- `scripts/diagnostics/make_support_bundle.py`
  - `--home=<state_root>` (defaults to current directory)
  - `--instance=<instance_id>`
  - `--output=<bundle.zip|bundle.tar.gz>`
  - `--format=zip|tar.gz`

See `docs/launcher/BUILD_AND_PACKAGING.md` for packaging determinism principles and `docs/launcher/SECURITY_AND_TRUST.md` for trust considerations.