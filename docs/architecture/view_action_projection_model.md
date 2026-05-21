Status: DERIVED
Last Reviewed: 2026-05-22
Supersedes: none
Superseded By: none
Stability: provisional
Task: COMMAND-RESULT-VIEW-SLICE-01

# View, Action, Projection Model

The reusable presentation surface is:

```text
result | document | snapshot
-> view
-> action
-> projection
-> shell
```

## View

A view is a semantic presentation model over a result, document, or snapshot. It
declares fields, sections, diagnostics, evidence, capability requirements, and
available actions. A view is not authority.

## Action

An action is an operation available from a view. Runtime actions should normally
be backed by commands. Contract-only actions are allowed when the system needs a
stable semantic affordance before handlers exist.

Actions must describe enablement, disabled reason, danger level, confirmation
policy, transaction policy, refusal behavior, and evidence behavior.

## Projection

A projection adapts a semantic view to a surface:

- `cli`
- `text`
- `rendered`
- `native`
- `headless`

Projection kinds are not separate semantic worlds. They must preserve command
result/refusal/diagnostic/evidence meaning.

## Shell

A shell is a product host such as Workbench, client, setup, launcher, server, or
CLI tooling. A shell may present projections. It does not own command truth.
