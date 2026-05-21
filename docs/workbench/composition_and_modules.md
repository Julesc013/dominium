Status: DERIVED
Last Reviewed: 2026-05-22
Supersedes: none
Superseded By: none
Stability: provisional

# Workbench Composition And Modules

Workbench is one consumer of the composition and module system. It can present
composition plans, decisions, lockfiles, diagnostics, refusals, limitations, and
evidence. It does not override composition decisions and does not become
semantic authority.

## Composition Use

Workbench may use composition surfaces to show:

- selected providers
- mounted packs
- enabled modules
- capability decisions
- refusal and degradation reports
- trust and compatibility reports
- lockfile evidence
- fixture-only or planned status

Workbench presentation must preserve the decision status. A planned or
fixture-only decision cannot be rendered as supported product behavior.

## Module Enablement

Workbench modules are descriptor-based. Module identity is `module_id`, not a
folder path. Enabling a Workbench module requires declared capabilities,
commands, views, documents, services, providers, diagnostics, refusals, and
evidence as applicable.

A module plan lock records requested modules, available modules, enabled
modules, refused modules, required capabilities, optional capabilities,
document/view/command contributions, required services/providers, diagnostics,
and evidence.

## Refusal Presentation

Workbench may present refusals and degradations, but it may not suppress them or
silently substitute another provider, module, pack, profile, or capability.
Every degraded decision must expose fallback trace and diagnostics.

## AIDE Use

AIDE may consume composition reports for routing and compact task context. That
does not expand the allowed path set for a task and does not let AIDE treat
derived lockfiles as canonical doctrine.

## Non-Goals

COMPOSITION-RESOLVER-LAW-01 does not implement the Workbench shell, workspace
runtime, module loader, rendered UI, package mounting, provider runtime,
renderer backend, platform backend, gameplay behavior, or release publication.
