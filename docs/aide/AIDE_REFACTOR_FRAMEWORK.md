# AIDE Refactor Framework

## Status

- Status: PROVISIONAL
- Phase: AIDE-STRUCTURE-00

## Purpose

The AIDE refactor framework makes future Dominium restructuring mechanical,
validated, reversible, and evidence-backed. It prevents ad hoc folder movement
by requiring inventories, classifications, maps, validation, and ledger entries
before any root recycling task changes paths.

## AIDE Role

AIDE is the restructuring control plane. It records plans, evidence, policies,
schemas, and validation results. Dominium architecture remains Dominium
architecture, and product/runtime behavior is not owned by AIDE paths.

## Non-Goals

- no product feature implementation
- no root moves in AIDE-STRUCTURE-00
- no deletion or archive application
- no active path aliases
- no build, package, release, provider, or network execution
- no renaming of XStack/AuditX/RepoX/TestX

## Refactor Lifecycle

The lifecycle is:

```text
inventory -> classify -> salvage_map -> move_map -> reference_rewrite -> validate -> build_test -> evidence -> shim_retire
```

Each phase produces evidence. Later phases may not infer approval from earlier
planning artifacts.

## File Fate Model

Future file-level classification must use these fates:

- `keep`: retain as-is under its current owner.
- `adapt`: keep useful behavior but adapt references or wrappers.
- `extract`: split useful material from a mixed file or root.
- `convert`: transform format or representation with explicit validation.
- `archive`: move only after archive/provenance approval.
- `drop`: remove only after explicit deletion approval and proof that identity,
  references, and history are preserved elsewhere.

## Move Map Model

A move map records source paths, target paths, actions, reasons, identity risk,
build sensitivity, references to rewrite, required validators, rollback notes,
and approval status. A move map is not executable approval until a reviewed task
promotes it.

## Salvage Map Model

A salvage map is required for mixed roots. It classifies each file or embedded
item by fate, target path, risk, and validators. It exists to prevent useful
legacy material from being lost or moved under the wrong owner.

## Path Alias Model

A path alias is a temporary compatibility plan. Active aliases are disabled by
default. Every alias needs a retirement condition, validation plan, consumers,
and proof that it does not redefine identity.

## Evidence Ledger Model

The migration ledger records what was planned, applied, not applied, renamed,
not renamed, aliased, or retired. It is the audit trail for future recovery and
changelog reconstruction.

## Validation Model

Future move waves should run, at minimum:

- AIDE doctor, validate, test, and selftest
- AIDE roots/repo/tools validators
- move-map and salvage-map schema checks
- strict repo, root allowlist, distribution, and component validators
- docs/build/UI/ABI checks where affected
- targeted build or test proof when source, build, runtime, or contracts are
  touched
- `git diff --check`

## Agent Instructions

- Do not move files before a salvage map and move map exist.
- Do not treat temporary paths as identity.
- Do not execute unknown tools.
- Do not delete or rename old tools before wrappers exist.
- Do not create new top-level roots without constitution review.
- Preserve XStack/AuditX/RepoX/TestX as evidence assets until adapters and
  retirement plans are proven.

## Next Tasks

- AIDE-STRUCTURE-01: Existing Tool Recycling Inventory; records tool fates,
  risks, and wrapper candidates without execution.
- AIDE-STRUCTURE-02: Wrap Existing Checks Through AIDE Commands.
- AIDE-ROOT-00: Root Recycling Framework and Salvage Map System.
- POST-CONVERGE-10F: Unit Annotation and RepoX Rule Remediation through
  AIDE-controlled evidence.
