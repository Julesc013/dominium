Status: CANONICAL
Last Reviewed: 2026-02-14
Supersedes: none
Superseded By: none

# XStack Extension Model

## Purpose

This model defines how optional X systems integrate with XStack without coupling core gate behavior to any specific tool family.

## Extension Contract

An extension must provide a `register_extensions()` function in `tools/xstack/extensions/<extension_id>/extension.py`.

Each registered descriptor must include:

- `extension_id`
- `runner` implementing the XStack runner protocol (`BaseRunner`)
- `artifact_contract` (deterministic artifact paths emitted by the extension)
- `scope_subtrees` (governed source scope touched by the extension)
- `cost_class` (`low|medium|high|critical`)

## Runtime Behavior

- Core runner resolution loads built-in runners first, then extension runners.
- Unknown runner IDs never block core execution; fallback behavior remains deterministic.
- Extension metadata participates in plan-hash inputs via runtime runner registry definitions.
- Extension ordering is deterministic (sorted by `extension_id`, then `runner_id`).

## Governance Rules

- Extensions must not modify FAST/STRICT/FULL semantics.
- Extensions must not introduce tracked-write side effects outside snapshot policy.
- Extensions must keep run-meta under workspace-scoped cache roots.
- Extensions must publish deterministic `version_hash()` implementations for cache invalidation.

## Example Stub

- Path: `tools/xstack/extensions/example_x/extension.py`
- Runner ID: `examplex_runner`
- Artifact contract: `docs/audit/examplex/EXAMPLEX_REPORT.json`
- Scope: `tools/`, `docs/`
- Cost class: `low`
