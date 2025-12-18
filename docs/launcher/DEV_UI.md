# Dev UI (Schema‑Driven DUI Launcher)

Doc Version: 2

This repository includes a temporary, fast “classic launcher” control surface intended for daily development. It is implemented via DUI (schema + state + events) so the same UI runs on:

- `--ui=native`
- `--ui=dgfx`
- `--ui=null` (headless; used for smoke tests)

Non‑goals: authentication, online news, store/updates, theming, custom widgets.

## Files

- UI schema (runtime loaded): `source/dominium/launcher/ui_schema/launcher_ui_v1.tlv`
- Schema generator (authoritative): `scripts/gen_launcher_ui_schema_v1.py`
- UI “app” (state render + event dispatch + tasks): `source/dominium/launcher/dom_launcher_app.cpp`
- Local news source (optional): `docs/launcher/news.txt`

## How It Works

The launcher UI is schema‑driven:

1. The UI layer loads the TLV schema at runtime.
2. Each frame, the UI layer builds a TLV “state snapshot” from launcher snapshots/caches.
3. DUI backends render that state (native, dgfx, or null).
4. DUI events (`ACTION`, `VALUE_CHANGED`) are translated into launcher actions.
5. Long operations run as UI tasks (no blocking UI), surfacing progress + outcome + refusal reasons.

The launcher core remains UI‑agnostic: the UI never changes core semantics; it only dispatches existing core operations and shows their results.

## Tabs and Workflows

- **Play**
  - Select target: `game` or `tool:<tool_id>` (from `tools_registry.tlv`)
  - Actions: Play, Safe Mode Play, Verify/Repair
  - Readouts: profile/backends, manifest hash (short), selection summary line, last run summary
- **Instances**
  - Actions: create (template/empty), clone, soft delete (confirm), import, export (definition/full), mark known‑good
- **Packs**
  - Enable/disable + update policy edits are staged; press Apply to commit a transaction
  - Resolver failures show dependency/conflict refusal reasons
- **Options**
  - GFX backend / renderer API / window overrides
  - Reset graphics overrides requires confirmation
  - Details dialog shows the effective override view
- **Logs / Diagnostics**
  - Shows recent runs and per‑run audit lines
  - Diagnostics bundle exports a full instance bundle and adds last‑run artifacts (handshake, launch_config, selection_summary, exit_status, audit_ref) when present

## Unified Selection Summary

The UI status bar displays a compact selection line derived from the per-run `selection_summary.tlv` artifact:

- It is the same source of truth used by:
  - CLI `launch` / `safe-mode` output (`selection_summary.line`)
  - CLI `audit-last`
  - `diag-bundle` summary export (`last_run_selection_summary.txt`)

See `docs/launcher/ECOSYSTEM_INTEGRATION.md` for the schema and invariants.

## Running

From a build output directory containing `dominium-launcher`:

- Native UI: `dominium-launcher --ui=native`
- DGFX UI: `dominium-launcher --ui=dgfx`
- Headless: `dominium-launcher --ui=null`

If you use a custom home/state root:

- `dominium-launcher --home=<path> --ui=native|dgfx|null`

## Smoke Tests

UI smoke tests are non‑interactive and validate the schema‑driven app layer.

- Build + run via CTest:
  - `ctest --test-dir build -C Debug -R dominium_launcher_ui_smoke_tests --output-on-failure`

The smoke test covers:

- `ui=null`: load schema, enumerate/select instance, invoke verify, launch a tool and confirm handshake/audit files exist
- `ui=dgfx`: create a headless window, render one frame, exit

## Extending the Schema Safely

Rules of thumb:

- Keep widget/action IDs stable; update `scripts/gen_launcher_ui_schema_v1.py` rather than hand‑editing IDs.
- Add new bindings and actions as additive changes (older schemas should keep loading).
- Update `dom_launcher_app.cpp` in two places:
  - State build: add new bound values to the TLV state snapshot
  - Event handling: translate new actions/values into existing launcher core operations
- Do not introduce filesystem or instance‑semantics logic into the UI layer; route through launcher core ops and surface audit/refusal reasons.
