Status: CANONICAL
Last Reviewed: 2026-02-01
Supersedes: none
Superseded By: none

# Application Layer Canon (APP-CANON0)

Scope: setup / launcher / client / server / tools.

## Prime directives
- Applications are orchestration shells: content-agnostic, rule-agnostic, authority-agnostic.
- Applications never mutate authoritative world state.
- Applications never implement simulation logic.
- Applications never bypass law, authority, epistemics, or SRZ.
- Applications never invent defaults or silently repair.

## Contract surface
- All applications communicate only via dom_contracts headers under `libs/contracts/include/dom_contracts/`.
- Contracts are POD, explicit version fields, TLV/JSON friendly, deterministic ordering.
- Contracts avoid engine/game headers beyond shared core types.

## Shared appcore
- All applications reuse `libs/appcore/` modules for discover/profile/repox/invoke/validate/command/output.
- UI code is excluded from appcore.

## Command graph
- CLI command graph is canonical.
- TUI/GUI are views over the same command registry.
- No UI-only actions are allowed.

## UI IR
- UI rendering is driven by UI IR schemas under `schema/ui/`.
- Strings are externalised; locale packs are normal packs.
- Accessibility is mandatory (keyboard, screen reader tags, resizable layouts).

## Application roles
- Setup: only application that mutates installation state.
- Launcher: reference shell for instances and packs; no direct mutation.
- Client: rendering, input, inspection, replay viewing.
- Server: headless authoritative orchestration and verification.
- Tools: read-only by default; write requires explicit flags.

## Failure behavior
- Applications never hide errors or warnings.
- Failures emit structured, machine-readable reports.

## Acceptance checklist
- Runs with zero content packs.
- CLI/TUI/GUI parity preserved.
- All strings externalised.
- RepoX metadata visible.
- Broken installs inspectable.
- No simulation logic exists.
- Tools are read-only by default.
- TestX passes deterministically.
