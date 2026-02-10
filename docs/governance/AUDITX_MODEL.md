Status: DERIVED
Last Reviewed: 2026-02-10
Supersedes: none
Superseded By: none

# AuditX Model

AuditX is the semantic audit axis in the governance stack.

## Responsibilities

- RepoX enforces structural invariants.
- TestX validates runtime behavior.
- AuditX reports semantic drift, debt, and ambiguity.

AuditX findings are advisory by default. Promotion from AuditX finding patterns into RepoX invariants or TestX regressions is explicit governance work.

## Findings Contract

- Findings are deterministic and machine-readable.
- AuditX is non-gating by default.
- AuditX emits reports; it does not auto-mutate runtime code.
- Findings include stable IDs, fingerprints, confidence, severity, classification, and recommended action.

## Finding Fields

Each finding record contains:

- `finding_id`
- `category`
- `severity`
- `confidence`
- `status`
- `location`
- `evidence`
- `suggested_classification`
- `recommended_action`
- `related_invariants`
- `related_paths`
- `created_utc` (informational; excluded from fingerprint)
- `fingerprint`

## Classification Buckets

- `CANONICAL`
- `SUPERSEDED`
- `PROTOTYPE`
- `LEGACY`
- `INVALID`
- `TODO-BLOCKED`

## Analyzer Model

Analyzers are modular plugins that consume the shared analysis graph and emit finding lists. Initial analyzers:

- A1 Reachability / orphaned code
- A2 Ownership boundary
- A3 Canon drift
- A4 Schema usage
- A5 Capability misuse
- A6 UI parity / bypass
- A7 Legacy contamination
- A8 Derived artifact freshness smell

## Shared Analysis Graph

- Graph nodes: files, symbols, commands, schemas, packs, tests, products.
- Graph edges: includes/imports, command bindings, schema usage, pack dependencies.
- Traversal and graph hashing are deterministic.

## Outputs

`auditx scan` writes DERIVED artifacts under `docs/audit/auditx/`:

- `FINDINGS.json`
- `FINDINGS.md`
- `SUMMARY.md`
- `INVARIANT_MAP.json`

## Promotion Path

AuditX findings may drive:

1. RepoX invariants for static enforcement.
2. TestX regressions for runtime behavior.
3. Docs updates where normative behavior lacks enforcement anchors.

## Usage

- `python tools/auditx/auditx.py scan --repo-root .`
- `python tools/auditx/auditx.py scan --repo-root . --changed-only`
- `python tools/auditx/auditx.py verify --repo-root .`
- `python tools/auditx/auditx.py enforce --repo-root .` (reserved, returns `refuse.not_enabled`)
