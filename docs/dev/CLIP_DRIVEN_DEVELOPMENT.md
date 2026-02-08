Status: DERIVED
Last Reviewed: 2026-02-08
Supersedes: none
Superseded By: none

# Clip-Driven Development

## Purpose

- Convert recordings and voice notes into governed, testable bug artifacts.
- Keep implementation work tied to reproducible evidence.

## Artifact Format

- Bug report artifacts are stored at `data/logs/bugreports/<id>.json`.
- Schema: `schema/bugreport.observation.schema`.
- Required fields include:
  - `id`
  - `observed_at_utc`
  - `expected_behavior`
  - `observed_behavior`
  - `build_identity`
  - one evidence source: `clip_path` or `voice_note_path`

## Ingestion Workflow

1. Capture evidence clip or voice note.
2. Run `tools/bugreport/ingest.py` with explicit metadata.
3. Validate generated JSON against schema.
4. Add regression test or mark deferred with explicit reason.

## Governance Rules

- RepoX rule `INV-BUGREPORT-RESOLUTION` fails if resolved reports lack:
  - `regression_test`, and
  - `defer_reason`.
- `defer_reason` requires explicit justification text.
- Silent closure of reports is forbidden.

## Minimal Command Example

```powershell
python tools/bugreport/ingest.py `
  --id BR-001 `
  --expected "observer mode denied without entitlement" `
  --observed "observer mode accepted in normal play" `
  --build-identity-file build/artifact_identity.preview.json `
  --clip clips/br-001.mp4 `
  --output data/logs/bugreports/BR-001.json
```

