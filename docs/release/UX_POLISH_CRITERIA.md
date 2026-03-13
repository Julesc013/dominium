Status: DERIVED
Last Reviewed: 2026-03-14
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: DIST
Replacement Target: release-facing UX criteria regenerated from DIST-5 tooling and release readiness policy

# UX Polish Criteria

## Purpose

DIST-5 defines the final user-facing polish bar for `v0.0.0-mock`.
It does not add features. It standardizes help text, menu wording, refusals,
and status output across CLI, TUI, rendered UI, and optional native adapters.

## Tone

- precise
- actionable
- brief by default
- explicit when refusing
- free of internal implementation jargon in default flows

## Failure Messaging

Every user-facing failure must include:

- a stable `refusal_code`
- a short human-readable reason
- one or more remediation hints with an exact next step where possible

Examples of acceptable remediation wording:

- `Run \`help compat-status\` to inspect the stable command shape.`
- `Use \`setup install register <path>\` for installed mode.`
- `Provide a valid \`--peer-descriptor-file\` emitted by a product \`--descriptor\` command.`

## Default Presentation Rules

- Default flows should prefer product names, mode names, and action labels over
  registry ids, schema ids, and internal fingerprints.
- Internal ids may appear in:
  - `--verbose`
  - machine-readable JSON
  - admin or audit surfaces
- Default help and menu surfaces should always expose the next common action.

## Help Text Rules

- Help output must be deterministic.
- Commands must be grouped in a stable order.
- Shared commands must include practical examples for:
  - starting a session
  - verifying packs
  - exporting instances
  - capturing a repro bundle
- Help text should reference stable command forms, not repo-only scripts, unless
  the surface is explicitly a developer tool.

## Main Menu Rules

Each product must expose a coherent main-menu equivalent:

- CLI: common actions discoverable through help and console entry
- TUI: menu, console, logs, and status visible or reachable immediately
- rendered client: menu overlay with start, seed, instance/save selection, and console access
- optional native adapters: same command-driven flows when present

## Status Output Rules

- Status outputs must remain machine-readable.
- Human-readable fields such as `message` and `summary` should be present where practical.
- Default status output should avoid dumping internal ids unless they are required for remediation.

## Non-Goals

- no gameplay changes
- no silent fallback
- no hidden errors
- no truth mutation from UI polish code
- no nondeterministic wording or ordering
