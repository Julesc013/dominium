Status: DERIVED
Last Reviewed: 2026-05-21
Supersedes: none
Superseded By: none
Stability: provisional

# Command, View, Event, Refusal, And Evidence Spine

## Purpose

Dominium command surfaces are the typed behavior boundary between intent and
implementation. CLI, TUI, headless tools, server/admin surfaces, rendered UI,
Workbench, AIDE/Codex workflows, and tests must converge on registered
commands instead of calling private implementation paths as independent
authorities.

This document is the prose companion to
`contracts/command/command_surface.contract.toml`.

## Core Rule

Workbench is not authority. CLI is not separate authority. TUI is not separate
authority. Headless orchestration is not separate authority. AIDE/Codex is not
product authority.

The authority path is:

```text
intent
-> registered command
-> capability and refusal check
-> owning service or Process path
-> typed result, document, event, refusal, and evidence
-> presentation by CLI, TUI, Workbench, rendered UI, headless, AIDE, or tests
```

The same command ID must mean the same behavior across surfaces. Different
surfaces may present the result differently, but they must not redefine the
meaning of the command.

## Command Surface

A command is a stable, typed behavior surface. Each command entry declares:

- command ID, version, owner, stability, and kind
- input and result schemas
- refusal codes
- optional event outputs
- evidence packet schema where proof or validation is involved
- allowed presentation/orchestration surfaces
- required capabilities
- service owner
- proof, compatibility policy, and replacement policy

Command IDs are semantic IDs, not file paths. Reusable substrate commands use
`domino.*`; Dominium product or game commands use `dominium.*`.

Initial command surfaces are provisional. A command becomes stable only after
proof, compatibility policy, refusal policy, and replacement policy are present.

## Result Documents

Commands return typed result documents. Results are JSON-serializable and
UI-independent. The base result status values are:

- `ok`
- `warning`
- `refused`
- `error`

Results may reference diagnostics, evidence packets, and payload documents.
Presentation code consumes the result; it does not own result meaning.

## Views

Views present results or documents. Views are not authority and must not mutate
truth. CLI summaries, TUI panels, Workbench modules, rendered UI projections,
server/admin views, test views, and AIDE reports may all render the same result
through different projections.

If a view needs new data, the command/result contract must be extended or a new
command must be registered. The view must not reach around the command surface
to private state.

## Events

Events report progress, state transitions, warnings, diagnostics, refusal
details, and evidence links. Events do not replace the final command result.
Events are typed, owner-scoped, and tied to source commands.

Long-running commands may emit events while preserving a single final result
document.

## Refusals

Refusal is a lawful typed outcome, not exception text. Each refusal declares:

- code
- owner
- reason
- recovery action
- stability
- optional evidence reference

The command-level scaffold lives in
`contracts/refusal/refusal_code.registry.json`. The full diagnostic and refusal
registries remain owned by later Foundation Lock tasks.

## Evidence

Evidence packets record command ID, run ID, inputs, outputs, diagnostics, proof
files, and validation context. Evidence is proof output, not source truth.

Validation, test, package, and release commands require an evidence policy
because those commands are used to close tasks or promote artifacts.

## Workbench And Product Surfaces

Workbench modules must call registered commands or registered services. They
must not call private validators, file paths, or package internals directly as
the long-term design.

During transition, direct calls may still exist in implementation history, but
new governance must classify them as internal or legacy and target them for
replacement through registered commands.

## AIDE And Codex

AIDE/Codex may orchestrate commands, collect evidence, and summarize results.
They do not define product semantics. AIDE evidence points back to contracts,
commands, and validators.

## Adding Or Replacing Commands

To add a command:

1. Register the command in `contracts/command/command_surface.contract.toml`.
2. Define or reference input and result schemas.
3. Declare refusals and required capabilities.
4. State the service owner and allowed surfaces.
5. Add proof and evidence policy.
6. Update public-surface registration if the command becomes an exposed
   contract surface.
7. Run `tools/validators/contracts/check_command_surface.py`.

To replace or retire a command, update the registry with replacement policy,
retirement reason where applicable, and compatibility notes. Do not silently
rename command IDs or change result/refusal meaning.

## Non-Goals

This law does not implement a command runtime, Workbench UI, game feature,
package runtime, renderer behavior, or server authority path. It defines the
contract and validation surface that later tasks must use.
