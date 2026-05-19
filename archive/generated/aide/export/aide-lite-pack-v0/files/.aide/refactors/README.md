# AIDE Refactor Control Plane

`.aide/refactors/` contains no-apply refactor-control schemas and generated
dry-run planning artifacts.

The original Q39 surfaces remain preserved here. AIDE-STRUCTURE-00 adds the
Dominium repo constitution framework beside them so future structural changes
can be represented as inventories, file classifications, salvage maps, move
maps, path-alias plans, migration ledger records, rollback notes, risks,
validation plans, and evidence packets.

## Move Maps

A move map records a proposed source path, target path, action, reason, risk,
identity sensitivity, build sensitivity, reference rewrite plan, validators,
rollback notes, and approval status. A move map is not approval to move files.

## Salvage Maps

A salvage map is required before a mixed root is recycled. It classifies each
file or embedded item as `keep`, `adapt`, `extract`, `convert`, `archive`, or
`drop`, with target hints and validation requirements. A `drop` fate is not
delete approval.

## Path Aliases

A path alias is temporary compatibility evidence. AIDE-STRUCTURE-00 introduces
no active runtime or build aliases. Future aliases must have consumers,
validation, and retirement conditions before they can be promoted.

## Root Recycling

Root recycling is the AIDE-controlled sequence for removing transitional root
clutter without dragging folders around:

1. inventory a root,
2. classify every file conservatively,
3. scan references and identity/authority/runtime/build markers,
4. generate a draft salvage map,
5. reconcile candidate move waves,
6. draft a move plan,
7. apply only in a later approved move task.

The default posture is no-apply. `root_recycling.schema.json`,
`salvage_map.schema.json`, `move_map.schema.json`, and `path_aliases.toml`
all require draft/not-approved/no-apply handling until a later reviewed task
authorizes a specific wave.

## AIDE-STRUCTURE-00 Boundary

This task creates framework scaffolding only. It does not move files, delete
files, rewrite references, apply move maps, create active aliases, mutate
branches, mutate target repositories, execute unknown tools, or call
providers/models/network services.

Future tasks must create and validate maps before moving files.
