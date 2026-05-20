Status: DERIVED
Last Reviewed: 2026-05-21
Supersedes: none
Superseded By: none
Stability: provisional

# Capability Refusal Law

CAPABILITY-REFUSAL-LAW-01 defines how Dominium records capability requests,
selected capabilities, degradation, refusals, recovery actions, diagnostics, and
evidence. It applies to optional providers, renderers, platforms, package and
profile loading, Workbench modules, commands, setup/install planning, artifact
trust, server/runtime authority, and release gates.

The core rule is no silent fallback. A missing optional provider may degrade, but
the decision must say what was requested, what was selected, why degradation was
allowed, what diagnostic applies, and where evidence lives.

## Capability Model

A capability is a named, owned, versioned ability. Capability IDs are lowercase
dotted semantic IDs, not paths:

- `domino.render.software`
- `domino.platform.win32.window`
- `domino.storage.local`
- `dominium.workbench.validation`

Capabilities declare kind, owner, version, stability, scope, determinism impact,
security impact, platform constraints, dependencies, conflicts, proof, and notes.

## Requests

A capability request declares who is asking, which capability is requested,
whether it is required, acceptable degradation, context, and whether evidence is
requested.

If a required capability is missing, the result is a refusal. If an optional
capability is missing, the result may be explicit degradation or not-required.

## Decisions

Decision values are:

- `selected`
- `degraded`
- `refused`
- `unavailable`
- `not_required`

Selected decisions name the selected capability or provider. Degraded decisions
must name `degraded_from` and `degraded_to`. Refused and unavailable decisions
must include a refusal code, diagnostic, recovery, and evidence reference.

## Degradation

Degradation is a non-fatal fallback, never a hidden implementation choice.

Examples:

- Requested `domino.render.opengl`; selected `domino.render.software`.
- Requested audio; selected null audio.
- Requested native UI; selected CLI/TUI.
- Requested optional Workbench module; omitted with warning.

Each case requires diagnostic/evidence and compatibility/determinism impact.

## Refusal

A refusal is a typed decision outcome. It is not exception text. Refusal codes
declare owner, category, stability, summary, reason, recovery, diagnostic codes,
related capabilities, related commands, proof, and notes.

Initial refusal categories cover capability, command, artifact, schema,
provider, security, policy, platform, dependency, runtime, validation, and
release.

## Recovery

Recovery actions are machine-readable. Initial actions include
`install_provider`, `enable_pack`, `upgrade_schema`, `select_alternative`,
`run_migration`, `use_degraded_mode`, `disable_feature`, `inspect_evidence`,
`contact_support`, and `not_recoverable`.

## Relationships

Commands may declare required capabilities. Providers will later declare
provided capabilities in PROVIDER-MODEL-01. Artifacts and packs use capability
and refusal law for trust, schema, package, and mod decisions. UI surfaces show
capability/refusal results; they do not invent meanings.

This task does not implement runtime provider selection, renderer fallback,
package runtime, Workbench UI, or server authority behavior.
