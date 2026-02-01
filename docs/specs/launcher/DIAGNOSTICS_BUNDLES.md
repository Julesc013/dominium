Status: DERIVED
Last Reviewed: 2026-02-01
Supersedes: none
Superseded By: none

# DIAGNOSTICS_BUNDLES

Launcher diagnostics bundles are deterministic, privacy-safe archives intended for support and CI.

## Command
```
dominium-launcher diag-bundle <instance_id> --out=<path> [--mode=default|extended] [--format=zip|tar.gz]
```

- `--mode=default` (default): minimal, redacted bundle.
- `--mode=extended`: includes additional rolling logs and more recent runs/audits.
- `--format` is inferred from `--out` when omitted (`.zip` or `.tar.gz`).

## Contents (Default)
- `bundle_meta.tlv`: bundle metadata (version, mode, instance_id, build_id, git_hash, run_ids).
- `bundle_index.tlv`: stable list of files + sha256 hashes.
- `build_info.txt`: derived build info (deterministic).
- `audit/launcher_audit_*.tlv`: recent audit logs.
- `instance/manifest.tlv`
- `instance/config/config.tlv`
- `instance/known_good.tlv`
- `instance/payload_refs.tlv` (if present)
- `instance/launch_history.tlv`
- `instance/staging/*` (transaction/manifest/payload refs if present)
- `runs/<run_id>/events.tlv` (structured events)
- `runs/<run_id>/handshake.tlv`
- `runs/<run_id>/launch_config.tlv`
- `runs/<run_id>/audit_ref.tlv` (or legacy `launcher_audit.tlv`)
- `runs/<run_id>/selection_summary.tlv`
- `runs/<run_id>/exit_status.tlv`
- `runs/<run_id>/last_run_summary.tlv`
- `runs/<run_id>/caps.tlv`
- `logs/caps_latest.tlv` (if present)
- Pack/mod manifests referenced by the instance (when present).

## Contents (Extended)
- Everything from default mode.
- `instance/logs/rolling/events_rolling.tlv`
- `logs/rolling/events_rolling.tlv`
- More recent runs/audits (bounded).

## Determinism + Privacy
- Archives are created via `scripts/diagnostics/make_support_bundle.py` and `scripts/packaging/make_deterministic_archive.py`.
- Stable ordering, stable timestamps (`SOURCE_DATE_EPOCH`, default 0).
- No environment variables, usernames, machine names, or secrets by default.
- Paths are relative and redacted; no absolute user paths.