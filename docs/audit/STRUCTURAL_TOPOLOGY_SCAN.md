Status: DERIVED
Last Reviewed: 2026-03-16
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: DOC-CONVERGENCE
Replacement Target: canon-aligned documentation set for convergence and release preparation

# STRUCTURAL TOPOLOGY SCAN

Status: Draft  
Last Reviewed: 2026-03-04  
Source Run: `tools/governance/tool_topology_generate.py`

## 1. Topology Snapshot

- Deterministic fingerprint: `bba0415e9b8903af340a46ff4ee96f1ea2b05861104554d5e7f4a7e830a7c24a`
- Nodes: `2904`
- Edges: `192077`

Node classes:

- `tool`: 1246
- `schema`: 956
- `registry`: 222
- `process_family`: 213
- `policy_set`: 186
- `module`: 77
- `contract_set`: 4

Edge classes:

- `validates`: 140684
- `enforces`: 47120
- `consumes`: 2842
- `depends_on`: 1430
- `produces`: 1

## 2. Dependency Hotspots

Top module consumers (by `consumes` edges):

- `module:src` (414)
- `module:src/client` (171)
- `module:src/inspection` (113)
- `module:src/net` (102)
- `module:src/control` (101)

Top schema dependencies:

- `schema:schemas/port.schema.json` (62)
- `schema:schemas/tool.schema.json` (55)
- `schema:schemas/message.schema.json` (47)
- `schema:schemas/order.schema.json` (46)
- `schema:schema/process.schema` (43)

Top registry dependencies:

- `registry:interaction_action_registry` (215)
- `registry:materials` (14)
- `registry:blueprint_registry` (6)
- `registry:domain_registry` (6)
- `registry:process_registry` (6)

## 3. Structural Violations Scan

Requested checks and findings:

1. Domain-specific logic outside model registry:
- Found: 7 inline-response-curve sites still in runtime code.
- All 7 are explicitly recorded in `data/registries/deprecation_registry.json` with `INV-REALISM-DETAIL-MUST-BE-MODEL` extensions and replacement model IDs.

2. Direct state mutation outside process layer:
- No new hard failures introduced by this pass.
- Existing broader smell surface remains in AuditX (for example direct schedule mutation smell in runtime), but not introduced by this patch.

3. Cross-domain direct mutation:
- `INV-CROSS-DOMAIN-MUTATION-MUST-BE-MODEL` added and enforced in RepoX STRICT.
- Current RepoX STRICT run reports zero hits for this invariant.

4. Unregistered action or artifact:
- `INV-ACTION-MUST-HAVE-FAMILY` and `INV-INFO-ARTIFACT-MUST-HAVE-FAMILY` are now part of strict governance checks.
- Current RepoX STRICT run reports zero hits for both invariants.

## 4. Produced Artifacts

- `docs/audit/TOPOLOGY_MAP.json`
- `docs/audit/TOPOLOGY_MAP.md`
- `build/repox/repox_strict_refactor1.json`
- `build/auditx/auditx_strict_refactor1.json`
