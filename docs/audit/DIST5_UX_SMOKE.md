Status: DERIVED
Last Reviewed: 2026-03-14
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: DIST
Replacement Target: release UX smoke report regenerated from DIST-5 tooling

# DIST5 UX Smoke

## Summary

- result: `complete`
- violation_count: `0`
- fingerprint: `ab72e3dcc2b7e9afcb10493a45d1eb152a181928f80f74d729ae585ca084d459`

## Help Surfaces

- `client` -> returncode=`0` stable=`True` examples=`True`
- `dominium_client` -> returncode=`0` stable=`True` examples=`True`
- `dominium_server` -> returncode=`0` stable=`True` examples=`True`
- `engine` -> returncode=`0` stable=`True` examples=`True`
- `game` -> returncode=`0` stable=`True` examples=`True`
- `launcher` -> returncode=`0` stable=`True` examples=`True`
- `server` -> returncode=`0` stable=`True` examples=`True`
- `setup` -> returncode=`0` stable=`True` examples=`True`
- `tool_attach_console_stub` -> returncode=`0` stable=`True` examples=`True`

## Refusals

- `client.compat_status.invalid_peer` -> code=`refusal.io.invalid_args` remediation=`Provide a valid `--peer-descriptor-file` emitted by a product `--descriptor` command.`
- `launcher.install_status.missing_install` -> code=`refusal.install.not_found` remediation=`Use `setup install register <path>` for installed mode, or place `install.manifest.json` beside the product binaries for portable mode.`

## Status Outputs

- `client.compat_status` -> payload=`True` summary=`True`
- `launcher.install_status` -> payload=`True` summary=`True`
- `setup.install_status` -> payload=`True` summary=`True`

## TUI

- backend_id: `lite`
- show_help: `True`
- panels: `panel.console, panel.logs, panel.menu, panel.status`

## Rendered Client

- menu_title: `Dominium`
- console_overlay_available: `True`
- quick_actions: `Console, Instance, Save, Seed, Start`

## Violations

- none
