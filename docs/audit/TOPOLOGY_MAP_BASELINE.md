Status: DERIVED
Last Reviewed: 2026-02-28
Version: 1.0.0
Scope: ARCH-REF-2 topology map and semantic impact baseline.

# Topology Map Baseline

## Node/Edge Counts
- topology artifact: `docs/audit/TOPOLOGY_MAP.json`
- markdown summary: `docs/audit/TOPOLOGY_MAP.md`
- node_count: `1975`
- edge_count: `57482`
- deterministic_fingerprint: `0da759457af53afa35133e0bb8328a51305bd866b1668ce1b0d80c52eb2a4ec4`

## Major Subsystems Captured
- runtime module surfaces from `engine/`, `game/`, `client/`, `server/`, `platform/`, `src/`, `launcher/`, `setup/`
- tooling module surfaces from `tools/*`
- schema surfaces from `schema/**/*.schema` and `schemas/**/*.schema.json`
- registry surfaces from `data/registries/**/*.json`
- process-family best-effort discovery via deterministic `process.*` token scan
- policy-set and contract-set nodes inferred from registry payloads

## Semantic Impact Rules
- tool: `tools/governance/tool_semantic_impact.py`
- FAST selection integration:
  - `tools/xstack/testx/runner.py` now computes semantic impact after impact-graph subseting.
  - if semantic impact is uncertain, FAST deterministically falls back to full STRICT-style execution (`run_all=true`).
- enforced semantic triggers:
  - schema changes => strict verification requirement + CompatX test suite requirement
  - registry changes => registry compile/lockfile suite requirement
  - control-plane changes => multiplayer determinism envelope suite requirement
  - NetworkGraph/FlowSystem changes => logistics/interior/core graph-flow regression suites
  - epistemic-path changes => LOD/epistemic safety suites

## Enforcement Added
- RepoX invariants:
  - `INV-TOPOLOGY-MAP-PRESENT`
  - `INV-NO-UNDECLARED-SCHEMA`
  - `INV-NO-UNDECLARED-REGISTRY`
- AuditX analyzers:
  - `E106_UNDECLARED_SUBSYSTEM_SMELL` (`UndeclaredSubsystemSmell`)
  - `E107_UNDECLARED_SCHEMA_SMELL` (`UndeclaredSchemaSmell`)
  - `E108_UNDECLARED_REGISTRY_SMELL` (`UndeclaredRegistrySmell`)

## TestX Coverage Added
- `test_topology_map_deterministic`
- `test_topology_map_includes_all_schemas`
- `test_topology_map_includes_all_registries`
- `test_semantic_impact_outputs_stable`

## Known Limitations
- process-family detection remains best-effort token scanning; false positives/negatives are possible until explicit process family registries exist.
- dependency edges derived from text token matching are governance heuristics, not runtime dependency resolution.

## Gate Notes
- RepoX (`py -3 tools/xstack/repox/check.py --repo-root . --profile STRICT`):
  - PASS
  - `repox scan passed (files=1044, findings=1)` (`INV-AUDITX-REPORT-STRUCTURE` warning only).
- AuditX (`py -3 tools/xstack/auditx/check.py --repo-root . --profile STRICT`):
  - run complete / PASS status
  - `auditx scan complete (changed_only=false, findings=1017)` (warning findings reported).
- TestX full STRICT (`py -3 tools/xstack/testx/runner.py --repo-root . --profile STRICT --cache off`):
  - FAIL (`selected_tests=390`, multiple existing unrelated failures in strict suite).
- strict build (`py -3 tools/xstack/run.py strict --repo-root . --cache on`):
  - REFUSAL (`exit_code=2`)
  - blockers:
    - `01.compatx.check` refusal (`findings=164`)
    - `10.testx.run` fail (existing strict suite failures)
    - `13.packaging.verify` refusal (lab build validation refused)
  - report: `tools/xstack/out/strict/latest/report.json`
