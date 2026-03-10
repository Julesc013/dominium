Status: CANONICAL
Last Reviewed: 2026-03-11
Supersedes: none
Superseded By: none
Version: 1.0.0
Compatibility: Bound to `docs/canon/constitution_v1.md`, `docs/canon/glossary_v1.md`, `docs/appshell/APPSHELL_CONSTITUTION.md`, `docs/contracts/CAPABILITY_NEGOTIATION_CONSTITUTION.md`, and `docs/packs/PACK_VERIFICATION_PIPELINE.md`.

# Commands And Refusals

## Purpose

APPSHELL-1 defines the stable command and refusal UX for all Dominium products.

The command surface must remain deterministic, documented, and backward-stable.
Shared commands must mean the same thing across engine, game, client, server,
setup, launcher, and tool products.
Commands are registered declaratively and dispatched through the shared
AppShell command registry rather than product-local shell branches.
The phrase `deterministic output ordering` is normative for both runtime
command results and generated help/documentation surfaces.

## Command Naming Rules

Stable command vocabulary uses canonical nouns and verbs only.

Rules:

- use stable noun-first namespaces such as `packs`, `profiles`, `session`,
  `server`, `client`, `logic`, and `geo`
- use stable verbs such as `list`, `show`, `verify`, `build-lock`, `status`,
  `save`, `trace`, and `probe`
- avoid deprecated or non-canonical legacy mode-language or other hardcoded
  runtime-mode slang
- sort command listings by stable `command_path`

## Shared Root Commands

Every AppShell product exposes these shared root commands:

- `help`
- `version`
- `descriptor`
- `compat-status`
- `profiles`
- `packs`
- `verify`
- `diag`
- `console`

Alias rules:

- `profiles` aliases `profiles list`
- `packs` aliases `packs list`
- `verify` aliases `packs verify`
- `console` aliases `console enter`

## Namespaces

The stable namespaced command trees are:

- `packs list`
- `packs verify`
- `packs build-lock`
- `profiles list`
- `profiles show`
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

Namespace rules:

- command ordering is deterministic
- namespace declaration without a bound handler must refuse explicitly
- silent omission of a declared namespace is forbidden

## Refusal Structure

Command refusals must serialize as:

- `refusal_code`
- `reason`
- `remediation_hint`
- `details` optional and law/epistemic filtered

AppShell may also emit a nested compatibility/refusal payload for reuse by
legacy surfaces, but the APPSHELL-1 top-level refusal fields are normative.

## Exit Codes

Refusals map to stable exit-code ranges through `data/registries/exit_code_registry.json`
and `data/registries/refusal_to_exit_registry.json`.

Stable ranges:

- `0`: success
- `10..19`: usage and command-shape errors
- `20..29`: pack/profile/verification errors
- `30..39`: compatibility and contract errors
- `40..49`: transport / IO-shell errors
- `50..59`: law/debug/gated-command refusals
- `60..69`: internal shell failures

Exact refusal mappings override prefix-family mappings.

## Deterministic Output Rules

- command output ordering must be stable and ID-sorted
- list outputs sort by stable IDs or paths, never host enumeration order
- help output is generated from the command registry, not handwritten
- auto-generated command docs are derived from the same registry as runtime help

## Offline Operation

The APPSHELL-1 command plane remains offline-capable.

- `descriptor` uses CAP-NEG local descriptor data only
- `compat-status` uses endpoint descriptors only
- `packs verify` and `packs build-lock` use the PACK-COMPAT offline pipeline
- `profiles list/show` inspect local bundle surfaces only

## Unavailable Namespace Rule

If a namespace is declared but not yet bound in the current AppShell phase:

- command execution must refuse explicitly
- refusal code must remain stable
- remediation must direct the operator to the shared command surface or a later
  phase rather than silently dropping the request
