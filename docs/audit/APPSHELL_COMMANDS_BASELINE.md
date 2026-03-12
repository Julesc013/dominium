Status: DERIVED
Last Reviewed: 2026-03-11
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: DOC-CONVERGENCE
Replacement Target: canon-aligned documentation set for convergence and release preparation

# AppShell Commands Baseline

## Scope

APPSHELL-1 establishes the deterministic command and refusal baseline for the
shared product shell.

The baseline covers:

- declarative command registration
- structured refusals with remediation
- stable refusal-to-exit mapping
- generated CLI reference output

## Shared Root Commands

The shared root surface is:

- `help`
- `version`
- `descriptor`
- `compat-status`
- `profiles`
- `packs`
- `verify`
- `diag`
- `console`

Aliases remain explicit:

- `profiles` -> `profiles list`
- `packs` -> `packs list`
- `verify` -> `packs verify`
- `console` -> `console enter`

## Product Namespace Baseline

Reserved stable namespaces are present in the registry for:

- `session.*`
- `engine.*`
- `game.*`
- `client.*`
- `server.*`
- `setup.*`
- `launcher.*`
- `logic.*`
- `geo.*`
- `tool.*`

In APPSHELL-1, unbound namespaces refuse explicitly instead of silently
disappearing.

## Refusal And Exit Summary

Runtime refusals serialize:

- `refusal_code`
- `reason`
- `remediation_hint`
- `details`

Stable exit families remain:

- `10..19` usage / command-shape errors
- `20..29` pack / profile / verification failures
- `30..39` compatibility / contract failures
- `40..49` IO / host-shell failures
- `50..59` law / debug / gated-command refusals
- `60..69` internal shell failures

Exact mappings in `data/registries/refusal_to_exit_registry.json` override
family-prefix mappings.

## Auto-Documentation

`tools/appshell/tool_generate_command_docs.py` generates
`docs/appshell/CLI_REFERENCE.md` directly from:

- `data/registries/command_registry.json`
- `data/registries/refusal_to_exit_registry.json`

This keeps runtime help and published CLI reference on the same deterministic
source.

## Validation Summary

APPSHELL-1 FAST validation covers:

- deterministic `help` output
- refusal-to-exit mapping stability
- offline `packs verify`
- `compat-status` output shape
- deterministic CLI doc generation

## Readiness

APPSHELL-1 is ready for APPSHELL-2 logging and APPSHELL-3 TUI panel work.
