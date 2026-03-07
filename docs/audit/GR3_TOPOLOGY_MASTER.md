# GR3 Topology Master

Source artifact: `docs/audit/TOPOLOGY_MAP.json`  
Generated via: `python tools/governance/tool_topology_generate.py --repo-root .`

## Snapshot
- Deterministic fingerprint: `3fe1464babc3c42ae4b2589351fb639ab1fd8839e0e8417b92c4fc2370940250`
- Node count: `3887`
- Edge count: `495175`

## Node Class Coverage
- `schema:*` nodes: `1114`
- `registry:*` nodes: `287`
- `contract_set:*` nodes: `120`
- `module:*` nodes: `84`
- `tool:*` nodes: `1679`

## Contract-Critical Presence Checks
- `registry:compute_budget_profile_registry`: present
- `registry:compute_degrade_policy_registry`: present
- `registry:reference_evaluator_registry`: present
- `registry:state_vector_registry`: present
- `registry:coupling_contract_registry`: present

## Contract Registry Cardinality
- Coupling contracts: `21` (`data/registries/coupling_contract_registry.json`)
- Tier contracts: `23` (`data/registries/tier_contract_registry.json`)
- Explain contracts: `72` (`data/registries/explain_contract_registry.json`)
- State vector definitions: `3` (`data/registries/state_vector_registry.json`)
- Compute budget profiles: `3` (`data/registries/compute_budget_profile_registry.json`)
- Reference evaluators: `6` (`data/registries/reference_evaluator_registry.json`)

## Integrity Notes
- Topology graph includes the new META-COMPUTE-0 schema/registry nodes.
- Contract-set families represented in topology are predominantly `coupling`, `tier`, and `explain`.
- This report is structural only; gate outcomes are tracked in `GR3_FAST_RESULTS.md`, `GR3_STRICT_RESULTS.md`, and `GR3_FULL_RESULTS.md`.
