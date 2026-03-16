Status: DERIVED
Last Reviewed: 2026-03-16
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: DOC-CONVERGENCE
Replacement Target: canon-aligned documentation set for convergence and release preparation

# Global Topology Review

Date: 2026-03-05
Scope: GLOBAL-REVIEW-0 topology and semantic-impact rebuild.

## Commands Run

- `python tools/governance/tool_topology_generate.py --repo-root .`
- `python tools/governance/tool_semantic_impact.py --repo-root . --topology-map docs/audit/TOPOLOGY_MAP.json --changed-file data/registries/constitutive_model_registry.json --changed-file data/registries/quantity_bundle_registry.json --changed-file data/registries/safety_pattern_registry.json --changed-file data/registries/coupling_contract_registry.json --changed-file data/registries/tier_contract_registry.json --changed-file data/registries/explain_contract_registry.json --out docs/audit/SEMANTIC_IMPACT_GLOBAL.json`

## Topology Rebuild Result

- `result`: complete
- `node_count`: 3290
- `edge_count`: 307709
- `deterministic_fingerprint`: `ee2d2181768dd1bf74e3e5410958e7175dddce9eaf3707521c7af3a58c2960c9`
- artifacts updated:
  - `docs/audit/TOPOLOGY_MAP.json`
  - `docs/audit/TOPOLOGY_MAP.md`

## Semantic Impact Rebuild Result

- output artifact: `docs/audit/SEMANTIC_IMPACT_GLOBAL.json`
- `result`: complete
- `deterministic_fingerprint`: `075a2eb245b8ba1c418676efa3519c1c95cc3717e424c531ba1e7c0b5a99f5de`
- changed anchors used:
  - `data/registries/constitutive_model_registry.json`
  - `data/registries/quantity_bundle_registry.json`
  - `data/registries/safety_pattern_registry.json`
  - `data/registries/coupling_contract_registry.json`
  - `data/registries/tier_contract_registry.json`
  - `data/registries/explain_contract_registry.json`

## Required Test Suites (semantic impact)

- `suite.contract.explain_engine`
- `suite.contract.registry_hard_gate`
- `suite.contract.tier_envelope`
- `suite.domain.elec`
- `suite.domain.field`
- `suite.domain.fluid`
- `suite.domain.mech`
- `suite.domain.mob`
- `suite.domain.phys`
- `suite.domain.sig`
- `suite.domain.therm`
- `suite.registry.compile`

## Notes

- This phase rebuilds topology and semantic-impact artifacts only; behavioral refactors are addressed in later phases.
