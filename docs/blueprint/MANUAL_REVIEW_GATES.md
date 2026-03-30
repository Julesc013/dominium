Status: DERIVED
Last Reviewed: 2026-03-31
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: PI
Replacement Target: snapshot-anchored manual review protocol after repository remapping

# Manual Review Gates

## Required Human Review Areas

| Gate | Why Human Review Is Required | Required XStack Profile | Required Artifacts |
| --- | --- | --- | --- |
| `licensing_commercialization_policy` | Policy shifts here can create legal and product obligations beyond technical validation. | `STRICT` | policy proposal; licensing impact summary; distribution change plan |
| `module_abi_boundaries` | ABI mistakes create silent breakage across loaders, sidecars, and long-lived compatibility layers. | `STRICT` | module boundary spec; ABI compatibility matrix; rollback coverage report |
| `runtime_privilege_escalation_policies` | Privilege policy changes can bypass law-gated authority or degrade operator trust. | `STRICT` | privilege policy diff; capability revocation plan; audit trail expectations |
| `architecture_graph_changes` | Changing the frozen architecture graph redefines module truth, ownership, and long-lived invariants. | `FULL` | architecture graph diff; module boundary diff; ControlX architecture change plan |
| `distributed_authority_model_changes` | Authority handoff and quorum semantics define what remains lawful in distributed execution. | `FULL` | authority handoff model; proof-anchor quorum plan; distributed replay verification design |
| `lifecycle_manager_semantics` | Lifecycle semantics control replacement, rollback, and state handoff, so mistakes become repo-wide failures. | `FULL` | lifecycle state machine; state handoff contract; rollback proof plan |
| `restartless_core_replacement_mechanisms` | Core replacement threatens the most fragile invariants and must not be green-lit by automation alone. | `FULL` | kernel replacement plan; state export and import proof; rollback and replay equivalence report |
| `semantic_contract_changes` | Contract changes alter lawful meaning, compatibility duties, and downstream schema expectations. | `FULL` | contract diff; migration or refusal plan; CompatX impact report |
| `trust_root_governance_changes` | Trust root rotation or policy changes alter who can deploy, verify, and recover. | `FULL` | trust policy diff; rotation choreography; downgrade and revocation proof |

