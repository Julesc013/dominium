Status: DERIVED
Last Reviewed: 2026-02-11
Supersedes: none
Superseded By: none

# AuditX Model

AuditX is the semantic radar axis in the governance stack.

## Responsibilities

- RepoX enforces structural invariants.
- TestX validates runtime behavior.
- AuditX reports semantic drift, debt, and ambiguity.

AuditX findings are advisory by default. Promotion from finding patterns into RepoX invariants or TestX regressions is explicit governance work.

## Findings Contract

- Findings are deterministic and machine-readable canonical artifacts.
- AuditX is non-gating by default.
- AuditX emits reports; it does not auto-mutate runtime code.
- Findings include stable IDs, fingerprints, confidence, severity, classification, and recommended action.
- Canonical findings do not carry run-time metadata (timestamps, host identifiers, scan IDs).

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

Expanded analyzers include:

- Duplicate concept
- Schema shadowing
- Capability drift
- Derived artifact contract
- Cross-pack dependency entropy
- Prompt drift
- Workspace contamination
- Blocker recurrence
- Security boundary and secret hygiene (SecureX integration)

## Shared Analysis Graph

- Graph nodes: files, symbols, commands, schemas, packs, tests, products.
- Graph edges: includes/imports, command bindings, schema usage, pack dependencies.
- Traversal and graph hashing are deterministic.
- Incremental caching reuses unaffected analyzer outputs when content hashes show partial changes.

## Outputs

`auditx scan` writes artifacts under `docs/audit/auditx/`:

- `FINDINGS.json` (`CANONICAL`)
- `INVARIANT_MAP.json` (`CANONICAL`)
- `PROMOTION_CANDIDATES.json` (`CANONICAL`)
- `TRENDS.json` (`CANONICAL`)
- `RUN_META.json` (`RUN_META`)
- `FINDINGS.md` (`DERIVED_VIEW`)
- `SUMMARY.md` (`DERIVED_VIEW`)

Canonical outputs are hash-stable and ordering-stable across rescans with identical semantic inputs.

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

## Self-Containment

- AuditX canonicalizes environment internally via `env_tools_lib`.
- AuditX supports execution from arbitrary CWD and from empty caller PATH.
- Workspace cache and trend history are stored under `tools/auditx/cache/<WS_ID>/`.
