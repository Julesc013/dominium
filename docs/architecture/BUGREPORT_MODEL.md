# Bugreport Bundle Model (BUG-0)

Status: FROZEN.

Purpose: Make every failure, desync, or crash reproducible, explainable, and actionable without changing simulation behavior.

## Canonical Bundle

The canonical bugreport bundle is a self-contained directory (or single-file container) that embeds a replay bundle and the minimal operational context needed to reproduce a defect.

Authoritative schema:
- `schema/bugreport.bundle.schema`

## Required Contents

Every bugreport bundle MUST contain:
- `replay_bundle_ref` (mandatory) for deterministic reproduction
- `install_manifest_ref` and `instance_manifest_ref`
- `runtime_descriptor_ref`
- `compat_report_ref`
- `ops_log_ref` (excerpt)
- `refusal_summary_ref`
- `environment_summary_ref`
- `created_at`
- `extensions`

Optional but supported:
- `save_bundle_ref`
- `reporter_notes_ref`
- `redaction_summary_ref`
- `content_index` for integrity validation

## Rules

- Bundles are immutable once created.
- Bundles are portable and self-contained.
- Bundles MUST NOT include executable code.
- Bundles MUST NOT bypass capability checks or sandbox policy.
- Redaction is allowed but MUST NOT alter replay or save bundles.
- Any redaction MUST be explicit and logged via `redaction_summary_ref`.

## Redaction & Privacy

Redaction is optional and data-only:
- Paths, usernames, and IP addresses MAY be removed or masked.
- Redaction MUST NOT modify replays or other deterministic artifacts.
- Redaction MUST be logged with counts and categories.

## Automated Capture Expectations

Tooling MUST support:
- Manual bundle creation on demand (CLI-first).
- Headless/server automation via the same CLI.
- CI artifact export for failing runs.

Automation must call the same bugreport bundle creation path used for manual capture.
