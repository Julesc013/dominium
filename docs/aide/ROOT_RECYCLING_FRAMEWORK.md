Status: DERIVED
Last Reviewed: 2026-05-16
Supersedes: none
Superseded By: none

# AIDE Root Recycling Framework

## Status

Draft/no-apply framework. Move application is not authorized.

## Purpose

Root recycling is evidence-backed extraction of useful material from transitional roots. It is not cleanup by appearance.

## Why Root Recycling Exists

Dragging root folders would break CMake, validators, manifests, pack/profile IDs, runtime assumptions, docs, and tests. AIDE makes cleanup mechanical: inventory, classify, scan, draft maps, review, then apply only after approval.

## No Wholesale Moves

Every file must be classified before any move wave.

## File Fate Model

Allowed fates are `keep`, `adapt`, `extract`, `convert`, `archive`, `drop`, and `preserve_unknown`. `drop` is never automatic deletion approval.

## Sensitivity Flags

Identity, build, runtime, security, safety, doctrine, generated, third-party, tool, test, authority, semantic, and ABI flags guide risk.

## Inventory

Inventories record files, directories, tracked state, size, first-line hints, kind hints, and sensitivity hints.

## Classification

Classifications are conservative. Unknown material remains `preserve_unknown`.

## Salvage Maps

Salvage maps are draft evidence with `apply_allowed = false` and `approval_status = not_approved`.

## Move Maps

Move maps are separate application plans and require explicit approval.

## Path Aliases

Aliases are disabled by default, temporary, not identity, and require an approved move map.

## Reference Scans

Reference scans record raw references only. They do not rewrite.

## Validation

Strict repo/root/distribution/component validators and supplemental docs/build/UI/ABI checks are required before any move.

## Evidence Ledger

Migration ledger entries record no moves/deletes/renames unless an explicit later task applies them.

## Agent Rules

Do not move, delete, rename, rewrite, approve maps, create active aliases, execute unknown tools, or change product behavior during inventory/reconciliation.

## Next Tasks

Use AIDE-MOVE-01-PLAN for a draft plan only after AIDE-GATE-01 passes.
