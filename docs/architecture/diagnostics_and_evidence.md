Status: DERIVED
Last Reviewed: 2026-05-21
Supersedes: none
Superseded By: none
Stability: provisional
Binding Sources: `contracts/diagnostic/diagnostic_policy.contract.toml`, `contracts/diagnostic/diagnostic_code.registry.json`, `contracts/evidence/evidence_packet.schema.json`, `contracts/refusal/refusal_code.registry.json`, `contracts/command/command_surface.contract.toml`

# Diagnostics And Evidence

Dominium diagnostics are stable machine-readable condition records, not log text.
They give CLI, TUI, Workbench, headless tools, tests, release proof, AIDE/Codex,
and server/admin surfaces a common way to name failures, warnings, refusals, and
proof outcomes.

Evidence packets are proof records. They can cite commands, diagnostics,
artifacts, output files, validation context, and provenance, but they are not
source authority unless a stronger contract explicitly promotes a fixture or
corpus.

## Core Rules

- A diagnostic has an ID, display code, owner, severity, category, stability,
  cause, recovery action, evidence expectation, and related surfaces where known.
- A refusal is a typed decision outcome. It may cite diagnostics, but it is not
  a free-text exception.
- A command result may cite diagnostics, refusals, events, and evidence packets.
- Events can carry progress and diagnostic references, but they do not replace
  the final command result schema.
- UI surfaces display diagnostics and evidence. UI is not authority over their
  meaning.
- AIDE/Codex may collect and summarize evidence. AIDE is not product authority.
- Free-text-only failures are not acceptable for stable or semi-stable surfaces.

## Registries

The diagnostic registry is
`contracts/diagnostic/diagnostic_code.registry.json`.

Severity values are owned by
`contracts/diagnostic/diagnostic_severity.registry.json`.

Category values are owned by
`contracts/diagnostic/diagnostic_category.registry.json`.

Policy is owned by `contracts/diagnostic/diagnostic_policy.contract.toml`.

The initial registry is conservative and provisional. It names foundational
conditions for repo layout, root allowlist, dependency direction, ABI header
hygiene, public-surface validation, command input/surface refusals, capability
absence, package manifests, schema version refusal, missing evidence, full-gate
debt, blocked AIDE tasks, and release promotion blockers.

## Evidence Packets

Evidence packets use `contracts/evidence/evidence_packet.schema.json`.

An evidence packet should identify:

- the subject being proven;
- the command, tool, or validator that produced the proof;
- diagnostic codes and status;
- inputs, outputs, files, and related artifacts;
- provenance such as repo commit and validation context.

Evidence status values include `pass`, `pass_with_warnings`, `fail`, `blocked`,
`not_run`, and `partial`. Command-facing legacy result status values are retained
for compatibility where the command surface already uses them.

## Refusals

Refusal codes remain in `contracts/refusal/refusal_code.registry.json`. This
task links existing command-level refusals to diagnostic codes where the mapping
is direct. The broader capability/refusal law remains a later Foundation Lock
task.

## Adding A Diagnostic

Add a diagnostic when a failure, warning, refusal, validation result, support
condition, or release blocker must be consumed by more than one surface or must
remain searchable across time.

A new diagnostic must declare an owner, severity, category, cause, recovery
action, evidence expectation, and stability. Stable diagnostics require stronger
proof and compatibility policy than provisional diagnostics.

## Retiring A Diagnostic

Do not delete diagnostic IDs casually. Mark a diagnostic `retired`, explain why,
name replacement diagnostics when applicable, and keep enough evidence for old
logs or support bundles to remain understandable.

## Presentation

Workbench, CLI, TUI, rendered UI, and headless reports may format diagnostics
differently. They must not rewrite diagnostic identity, severity, category,
recovery meaning, or evidence references.
