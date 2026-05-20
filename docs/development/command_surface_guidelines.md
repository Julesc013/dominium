Status: DERIVED
Last Reviewed: 2026-05-21
Supersedes: none
Superseded By: none
Stability: provisional

# Command Surface Guidelines

## When To Add A Command

Add a command when behavior needs to be invoked from more than one surface, when
it creates evidence, when it is part of a task closeout path, or when Workbench,
CLI, TUI, server/admin, tests, AIDE/Codex, or rendered UI need the same typed
operation.

Do not add a command to paper over a private implementation call. First identify
the owning service or Process path, then register the command as a typed
boundary over that owner.

## Naming

Use lowercase dotted semantic IDs:

- `domino.<area>.<verb>` for reusable substrate commands
- `dominium.<area>.<verb>` for Dominium product or game commands

Do not encode file paths, tools, implementation classes, or UI names in command
IDs.

Good examples:

- `dominium.repo.fast_strict.run`
- `dominium.public_surface.validate`
- `dominium.dependency_direction.validate`

Bad examples:

- `tools.validators.check_public_surface`
- `apps.workbench.button.run`
- `scripts/run-this-file`

## Schemas And Results

Every command needs an input schema and a result schema. Result documents must
be serializable to JSON and must be independent of presentation. Use
`contracts/result/result.schema.json` for provisional generic results until a
specific result schema is required.

Every result should make status explicit:

- `ok`
- `warning`
- `refused`
- `error`

Never make users or tools infer refusal from arbitrary stderr text.

## Refusals

Refusals are typed outcomes. A command should declare every refusal code it may
produce. Each refusal needs a reason and recovery path.

Command-level refusal scaffolding currently lives in
`contracts/refusal/refusal_code.registry.json`. Later diagnostic and
capability/refusal tasks own the full registry.

## Evidence

Validation, test, package, and release commands must declare an evidence schema.
Evidence packets are how AIDE/Codex, CI, and humans prove what ran. Evidence is
not source truth and must not replace contracts or schemas.

## Workbench

Workbench modules consume registered commands and result documents. They may
render richer views, but they must not redefine command behavior or bypass
refusal/capability gates.

If a Workbench feature needs private data, add a command or service contract
instead of calling private validators or implementation paths directly.

## AIDE And Codex

AIDE/Codex may invoke registered commands, collect evidence, and summarize
results. They must not claim a command exists unless it is registered, and they
must not turn a local tool path into a public command by convention.

## Adding A Command

1. Add a `[[command]]` entry under
   `contracts/command/command_surface.contract.toml`.
2. Choose a command kind from
   `contracts/command/command_kind.registry.json`.
3. Add or reference schemas.
4. Add refusal codes.
5. Declare allowed surfaces and service owner.
6. Add proof and compatibility notes.
7. Run:

```text
python tools/validators/contracts/check_command_surface.py --repo-root . --strict
```

For fixture changes, also run:

```text
python tools/validators/contracts/check_command_surface.py --repo-root . --fixtures
```

## What Not To Do

- Do not implement product behavior inside the command registry.
- Do not use command IDs as file paths.
- Do not mark commands stable without proof.
- Do not create Workbench-only authority.
- Do not make CLI, TUI, rendered UI, server/admin, AIDE, or tests define
  separate behavior for the same command.
- Do not hide failures by converting them to warnings unless the contract
  explicitly permits that warning.
