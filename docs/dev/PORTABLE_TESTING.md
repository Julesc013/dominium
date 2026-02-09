Status: DERIVED
Last Reviewed: 2026-02-09
Supersedes: none
Superseded By: none

# Portable Testing

## Scope

This document defines portable and installed test execution for setup/launcher
products.

## Portable Mode

Portable mode runs binaries/tools directly from realized output without setup
mutation:

- expected root example: `dist/sys/winnt/x64/`
- execution may start from any current working directory
- run inputs must be explicit (install root, manifests, lockfile references)

## Installed Mode

Installed mode is setup + launcher orchestration:

1. setup cache/install/rollback operations resolve install state.
2. launcher resolves instance and runs product mode.

Launcher is read-only over install state.

## Deterministic Refusal Expectations

Portable/install smoke tests assert deterministic refusal behavior. Current
required refusal identifiers:

- `REFUSE_INVALID_INTENT`
- `REFUSE_CAPABILITY_MISSING`
- `REFUSE_INTEGRITY_VIOLATION`

## Example Commands (WinNT x86_64 build output)

```
python tools/setup/setup_cli.py --help
python tools/launcher/launcher_cli.py --help
python tools/setup/setup_cli.py detect --install-root C:/tmp/dominium_install
python tools/launcher/launcher_cli.py preflight --install-manifest install.manifest.json --instance-manifest instance.manifest.json
```

All commands must behave deterministically for the same inputs.
