Status: DERIVED
Last Reviewed: 2026-02-08
Supersedes: none
Superseded By: none

# IRC-0 Phase 4: Interface Launch Report

## Method

- CLI verification:
  - `--help`
  - one minimal deterministic command (success or explicit refusal)
- TUI verification (where applicable):
  - `--ui=tui` launch and clean exit/refusal
- GUI verification (where applicable):
  - headless launch if supported
  - explicit refusal path accepted for intentional stubs

## Results

| Binary | CLI `--help` | Minimal command | TUI | GUI | Notes |
| --- | --- | --- | --- | --- | --- |
| `build/msvc-base/bin/setup.exe` | PASS | `prepare --root tmp/irc0_setup_root2` -> PASS | REFUSAL (`--ui=tui` exits 2 via setup_cli usage path) | REFUSAL (`setup: gui not implemented`) | deterministic refusal path present |
| `build/msvc-base/bin/launcher.exe` | PASS | `capabilities` -> PASS | PASS (`launcher: shutdown=app_request`) | PASS headless (`--ui=gui --headless --renderer null --ui-frames 1`) | no hidden logic observed |
| `build/msvc-base/bin/client.exe` | PASS | `--smoke` -> PASS (`MP0 client local hash`) | PASS (`client: shutdown=app_request`) | PASS headless (`--ui=gui --headless --renderer null --ui-frames 1`) | deterministic smoke hash emitted |
| `build/msvc-base/bin/server.exe` | PASS | `--smoke` -> PASS (`MP0 loopback hash`) | REFUSAL (`server: tui not implemented`) | REFUSAL (`server: gui not implemented`) | deterministic refusal path present |
| `dist/sys/winnt/x64/bin/tools/tool_ui_bind.exe` | PASS | `--repo-root . --ui-index tools/ui_index/ui_index.json --out-dir libs/appcore/ui_bind --check` -> PASS | N/A | N/A | canonical UI bind check passed |
| `dist/sys/winnt/x64/bin/tools/tool_ui_validate.exe` | PASS | `--input tools/launcher/ui/doc/launcher_ui_doc.tlv --tier win32_t1` -> deterministic validation errors | N/A | N/A | explicit structured errors, no crash |
| `tools/pack/pack_validate.py` | PASS | `--repo-root . --pack-root tmp/irc0_extension/org.dominium.test.integration_probe --format json` -> PASS | N/A | N/A | schema/manifest validation deterministic |

## Determinism / Refusal Observations

- All failures were explicit and deterministic (`not implemented`, CLI usage refusal, or structured validation errors).
- No implicit fallback behavior was observed in interface launch checks.
